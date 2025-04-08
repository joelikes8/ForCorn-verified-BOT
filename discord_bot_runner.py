"""
Specialized Discord bot runner for Replit

This script runs only the Discord bot component without starting 
the Flask web application. This allows the bot to be run in a 
separate workflow from the web interface.
"""

import os
import sys
import logging
import importlib.util
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord_runner")

logger.info("Starting Discord bot runner (NO WEB SERVER)")

# Check for Discord token
if not os.environ.get("DISCORD_TOKEN"):
    logger.critical("DISCORD_TOKEN not found in environment variables!")
    logger.critical("Please add your Discord bot token to the Secrets tab or .env file")
    sys.exit(1)

# Try to import and run the standalone bot directly
try:
    logger.info("Attempting to run standalone Discord bot...")
    # Check if standalone_discord_bot.py exists
    if os.path.exists("standalone_discord_bot.py"):
        # Use subprocess to run the standalone bot in a completely separate process
        logger.info("Found standalone_discord_bot.py, running as subprocess")
        subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
    else:
        logger.error("standalone_discord_bot.py not found!")
        sys.exit(1)
except Exception as e:
    logger.critical(f"Error running bot: {e}")
    import traceback
    logger.critical(traceback.format_exc())
    sys.exit(1)