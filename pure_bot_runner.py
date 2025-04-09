#!/usr/bin/env python3
"""
Pure Bot Runner

This script runs ONLY the Discord bot with no web server components at all.
It's designed to be completely isolated and avoids any imports from the
web application modules to prevent port conflicts.
"""

import os
import sys
import logging
import importlib.util
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("pure_bot")

# Set environment variables to ensure we're in bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["PORT"] = "9000"  # Use port 9000 for any HTTP components

logger.info("Starting Discord bot in pure isolated mode...")

# Try to load and run the standalone bot script
try:
    # Direct approach - import and run
    spec = importlib.util.spec_from_file_location("standalone_bot", "standalone_discord_bot.py")
    if spec and spec.loader:
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'main'):
            logger.info("Running standalone_discord_bot.py directly...")
            module.main()
            sys.exit(0)
except Exception as e:
    logger.error(f"Error importing standalone bot: {e}")

# If that fails, try to run it as a subprocess
try:
    logger.info("Falling back to subprocess execution...")
    subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
    sys.exit(0)
except Exception as e:
    logger.critical(f"Subprocess execution also failed: {e}")
    sys.exit(1)