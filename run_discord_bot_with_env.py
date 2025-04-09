#!/usr/bin/env python3
"""
Discord Bot Runner with Environment Variables

This script sets the necessary environment variables and then
runs the standalone Discord bot.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot_runner")

# Set the required environment variables
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true" 
os.environ["NO_WEB_SERVER"] = "true"

logger.info("Setting environment variables for Discord bot")
logger.info("DISCORD_BOT_WORKFLOW=true")
logger.info("BOT_ONLY_MODE=true")
logger.info("NO_WEB_SERVER=true")

# Try to import and run the bot
if os.path.exists("standalone_discord_bot.py"):
    logger.info("Found standalone_discord_bot.py, importing...")
    from standalone_discord_bot import main as run_bot
    logger.info("Starting bot...")
    run_bot()
else:
    logger.error("standalone_discord_bot.py not found!")
    # Try importing from main.py instead
    logger.info("Trying to run main.py...")
    import main
    # main.py should detect the environment variables we set and run the bot