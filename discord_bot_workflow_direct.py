#!/usr/bin/env python3
"""
Direct Discord Bot Workflow Runner

This script is ONLY for running the Discord bot in the workflow,
completely bypassing any imports from the web application.
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
logger = logging.getLogger("discord_bot_workflow")

def main():
    """Main function to start the Discord bot in workflow mode"""
    # Set environment variables
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    os.environ["PORT"] = "9000"
    
    # Print header
    logger.info("=" * 60)
    logger.info("STARTING DISCORD BOT IN DIRECT WORKFLOW MODE")
    logger.info("Completely isolated from web application")
    logger.info("=" * 60)
    
    # Run the standalone bot
    try:
        # Import and run directly
        logger.info("Importing standalone_discord_bot...")
        from standalone_discord_bot import main as run_bot
        run_bot()
    except Exception as e:
        logger.error(f"Failed to import standalone_discord_bot: {e}")
        logger.info("Trying to run as subprocess...")
        
        try:
            # Run as subprocess if import fails
            subprocess.run(
                ["python", "standalone_discord_bot.py"],
                check=True,
                env=os.environ
            )
        except Exception as subprocess_error:
            logger.critical(f"Failed to run subprocess: {subprocess_error}")
            sys.exit(1)

if __name__ == "__main__":
    main()