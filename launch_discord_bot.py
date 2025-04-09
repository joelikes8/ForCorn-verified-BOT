#!/usr/bin/env python3
"""
Discord Bot Launcher

This script launches the Discord bot directly, bypassing the Flask application.
It should be used to ensure the bot is properly logged in and showing online status.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bot_launcher")

def main():
    """Main function to launch the Discord bot"""
    logger.info("Launching Discord bot...")
    
    # Define the path to the Discord bot script
    bot_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "discord_bot_only_run.py")
    
    if not os.path.exists(bot_script):
        logger.error(f"Bot script not found: {bot_script}")
        return 1
    
    logger.info(f"Bot script path: {bot_script}")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env["BOT_ONLY_MODE"] = "true"
        env["NO_WEB_SERVER"] = "true"
        
        # Launch the Discord bot
        logger.info("Starting Discord bot process...")
        process = subprocess.Popen(
            [sys.executable, bot_script],
            env=env
        )
        
        logger.info(f"Bot process started with PID: {process.pid}")
        return 0
    except Exception as e:
        logger.error(f"Error launching Discord bot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())