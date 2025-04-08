#!/usr/bin/env python3
"""
Simple Discord Bot Starter for Render.com

This script provides a simpler approach to starting
the Discord bot on Render.com, focusing on basic functionality.
"""

import os
import sys
import logging
import time
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("discord_bot")

def main():
    """Directly run the bot with its own imports"""
    logger.info("Starting Discord bot...")
    
    # Check for Discord token
    if not os.environ.get("DISCORD_TOKEN"):
        logger.critical("DISCORD_TOKEN environment variable is missing")
        sys.exit(1)
    
    try:
        # Import the discord_main module and run it directly
        logger.info("Importing and running discord_main.py")
        import discord_main
        
        # Run the main function
        logger.info("Calling discord_main.main() function")
        discord_main.main()
            
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    retry_count = 0
    max_retries = 5
    
    while retry_count < max_retries:
        try:
            main()
            break  # Exit the loop if successful
        except Exception as e:
            retry_count += 1
            logger.error(f"Bot crashed (attempt {retry_count}/{max_retries}): {e}")
            
            if retry_count < max_retries:
                retry_delay = 10  # seconds
                logger.info(f"Restarting in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.critical(f"Bot failed after {max_retries} attempts. Giving up.")
                sys.exit(1)