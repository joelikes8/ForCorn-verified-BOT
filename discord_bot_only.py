#!/usr/bin/env python3
"""
Discord bot only script

This script runs only the Discord bot with absolutely no web components.
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
logger = logging.getLogger("discord_bot_only")

# Mark this as bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"

def main():
    """Main entry point for the Discord bot workflow"""
    logger.info("Starting Discord bot in bot-only mode")
    
    try:
        # Direct import from simple_discord_bot to avoid any webapp imports
        logger.info("Loading simple Discord bot...")
        from simple_discord_bot import run_bot
        logger.info("Successfully imported simple Discord bot")
        run_bot()
    except Exception as e:
        logger.critical(f"Critical error starting bot: {e}")
        import traceback
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()