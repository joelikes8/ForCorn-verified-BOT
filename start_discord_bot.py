#!/usr/bin/env python3
"""
Discord Bot Starter

This script is specifically designed to start the Discord bot correctly with
the proper environment variables. It will attempt to run the bot in the most
reliable way possible.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("start_discord_bot")

# Set environment variables to ensure we run in bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"

# Load environment variables from .env file if it exists
try:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Check if DISCORD_TOKEN is available
if not os.environ.get("DISCORD_TOKEN"):
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.critical("Please add your Discord bot token in the Secrets tab (🔑) or .env file")
    sys.exit(1)

# Start the bot using the most reliable method
logger.info("Starting Discord bot...")

# Try bot startups in order of preference
started = False

# 1. Try the main Discord bot first (full features)
if not started:
    try:
        logger.info("Attempting to start discord_main.py with full features...")
        from discord_main import main as run_discord_main
        run_discord_main()
        started = True
    except Exception as e:
        logger.warning(f"Could not start discord_main: {e}")

# 2. Try the standalone bot
if not started:
    try:
        logger.info("Attempting to start standalone_discord_bot.py...")
        from standalone_discord_bot import main as run_standalone_bot
        run_standalone_bot()
        started = True
    except Exception as e:
        logger.warning(f"Could not start standalone_discord_bot: {e}")

# 3. Try the simple Discord bot as last resort
if not started:
    try:
        logger.info("Attempting to start simple_discord_bot.py...")
        from simple_discord_bot import run_bot
        run_bot()
        started = True
    except Exception as e:
        logger.warning(f"Could not start simple_discord_bot: {e}")

# If all imports failed, try running them directly using subprocess
if not started:
    import subprocess
    logger.info("Attempting to run Discord bot using subprocess...")
    
    for script in ["discord_main.py", "run_discord_bot.py", "standalone_discord_bot.py", "simple_discord_bot.py"]:
        if os.path.exists(script):
            try:
                logger.info(f"Running {script} as subprocess...")
                subprocess.run([sys.executable, script], check=True)
                started = True
                break
            except subprocess.SubprocessError as e:
                logger.warning(f"Failed to run {script}: {e}")

if not started:
    logger.critical("Failed to start Discord bot in any way!")
    logger.critical("Please check your code and ensure Discord bot files are present.")
    sys.exit(1)