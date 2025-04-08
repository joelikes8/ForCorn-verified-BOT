"""
Discord bot runner script for the workflow

This script is specifically designed to run in the 'discord_bot' workflow
and start only the Discord bot component without the web application.
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
logger = logging.getLogger("discord_bot_workflow")

# Mark this as the discord bot workflow
os.environ["DISCORD_BOT_WORKFLOW"] = "true"

# Define the main function
def main():
    """Main entry point for the Discord bot workflow"""
    logger.info("Starting Discord bot in dedicated workflow")
    
    try:
        # Try to import and run the main Discord bot
        from discord_main import main as run_discord_bot
        logger.info("Successfully imported Discord bot")
        run_discord_bot()
    except Exception as e:
        logger.error(f"Error importing main Discord bot: {e}")
        try:
            # Try to fall back to the simple version
            logger.info("Falling back to simplified Discord bot")
            from simple_discord_bot import run_bot
            run_bot()
        except Exception as e2:
            logger.critical(f"Critical error starting bot: {e2}")
            print(f"Failed to start Discord bot: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()