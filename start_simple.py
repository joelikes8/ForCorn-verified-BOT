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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("start_simple")

def main():
    """Directly run the bot with its own imports"""
    logger.info("Starting ForCorn Discord Bot (Simple Version)")
    
    # Check for Discord token
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.error("DISCORD_TOKEN environment variable not set!")
        logger.error("Please set this variable in your environment and try again.")
        sys.exit(1)
    
    logger.info("Discord token found. Checking for dependencies...")
    
    # Import the simple bot module
    try:
        from simple_discord_bot import run_bot
        logger.info("Successfully imported bot module.")
        
        # Run the bot
        logger.info("Starting bot...")
        run_bot()
    except ImportError as e:
        logger.error(f"Failed to import bot modules: {e}")
        logger.error("Make sure you have all required dependencies installed.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    logger.info("=== ForCorn Simple Bot Starter ===")
    
    # Add retry mechanism
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            main()
            break  # Exit retry loop if successful
        except Exception as e:
            retry_count += 1
            logger.error(f"Attempt {retry_count}/{max_retries} failed: {e}")
            if retry_count < max_retries:
                sleep_time = 10 * retry_count
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.critical("All retry attempts failed. Exiting.")
                sys.exit(1)