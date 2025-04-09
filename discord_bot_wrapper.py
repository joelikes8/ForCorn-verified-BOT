#!/usr/bin/env python3
"""
Discord Bot Wrapper Script

This script is a wrapper that ensures the Discord bot is started correctly
when the discord_bot workflow is run. It first kills any existing web server
processes that might have been started by mistake, then runs the standalone bot.
"""

import os
import sys
import logging
import subprocess
import time
import signal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot_wrapper")

# Ensure we're in bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"

# Try to kill any running Flask servers on port 5000
try:
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        cmdline = ' '.join(proc.info['cmdline'] or [])
        if ('python' in cmdline and 'main.py' in cmdline) or 'flask' in cmdline or 'gunicorn' in cmdline:
            try:
                logger.info(f"Killing Flask/Gunicorn process: {proc.info['pid']}")
                os.kill(proc.info['pid'], signal.SIGTERM)
                time.sleep(0.5)  # Give it a chance to shut down
            except Exception as e:
                logger.warning(f"Error killing process: {e}")
except ImportError:
    # If psutil is not available, use a crude approach
    logger.warning("psutil not available, using basic process management")
    try:
        subprocess.run("pkill -f 'python.*main.py' || true", shell=True, check=False)
        subprocess.run("pkill -f 'gunicorn' || true", shell=True, check=False)
    except Exception as e:
        logger.warning(f"Error killing processes: {e}")

# Now run our specialized bot starter
logger.info("Starting Discord bot using start_discord_bot.py...")
try:
    # Use execv to replace the current process with the bot process
    os.execv(sys.executable, [sys.executable, 'start_discord_bot.py'])
except Exception as e:
    logger.critical(f"Failed to exec start_discord_bot.py: {e}")
    
    # Fallback: try running as a subprocess
    try:
        logger.info("Falling back to subprocess execution...")
        subprocess.run([sys.executable, 'start_discord_bot.py'], check=True)
    except Exception as e2:
        logger.critical(f"Critical failure - could not start bot: {e2}")
        sys.exit(1)