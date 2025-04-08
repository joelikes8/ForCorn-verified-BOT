#!/usr/bin/env python
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
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    """Directly run the bot with its own imports"""
    logger.info("Starting Discord bot in simple mode...")
    
    # Print environment information
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    logger.info(f"Files in current directory: {os.listdir('.')}")
    
    # Check if DISCORD_TOKEN is available
    if not os.environ.get("DISCORD_TOKEN"):
        logger.error("DISCORD_TOKEN environment variable not set")
        return 1
    
    # This approach uses a simpler method of running the bot's main.py
    try:
        logger.info("Importing and running main.py...")
        
        # Import the main function from main.py
        from main import main as run_bot
        
        # Run the bot's main function
        run_bot()
        
        return 0
    except Exception as e:
        logger.error(f"Error running bot: {e}")
        logger.exception("Traceback:")
        return 1

if __name__ == "__main__":
    sys.exit(main())
