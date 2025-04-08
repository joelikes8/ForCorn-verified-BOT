#!/usr/bin/env python3
"""
Discord bot starter script

This script is designed to be used with Replit workflows
to run the Discord bot without any web components.
"""

import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot")

if __name__ == "__main__":
    logger.info("Starting Discord bot via isolated_bot.py...")
    
    try:
        import isolated_bot
        logger.info("Bot startup successful")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)