#!/usr/bin/env python3
"""
Completely Isolated Bot Runner

This script runs a completely isolated Discord bot with no web app dependencies at all.
It explicitly sets environment variables and runs the standalone_discord_bot.py file.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("isolated_runner")

# Set environment variables to prevent port conflicts
os.environ["PORT"] = "9000"
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"

# Skip webapp import
os.environ["SKIP_WEBAPP"] = "true"

# Set PYTHONPATH to only include the current directory
os.environ["PYTHONPATH"] = "."

logger.info("Starting completely isolated Discord bot...")
logger.info(f"Environment variables: PORT={os.environ.get('PORT')}, DISCORD_BOT_WORKFLOW={os.environ.get('DISCORD_BOT_WORKFLOW')}")

# Run the standalone Discord bot in a subprocess
try:
    subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
except Exception as e:
    logger.critical(f"Failed to start bot: {e}")
    sys.exit(1)