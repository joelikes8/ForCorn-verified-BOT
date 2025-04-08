#!/usr/bin/env python3
"""
Discord Bot Entry Point

This script is designed to be the entry point for the Discord bot when run
in the discord_bot workflow. It has no dependencies on the web interface
and does not start a Flask server.
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
logger = logging.getLogger("discord_bot_main")

# Make it obvious we're in bot-only mode
logger.info("=" * 50)
logger.info("STARTING IN DISCORD BOT ONLY MODE")
logger.info("=" * 50)

# Set environment variables for child processes
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"

def main():
    """Main function to run the Discord bot"""
    try:
        # Try to import and run standalone bot directly
        logger.info("Starting standalone Discord bot...")
        try:
            # Try to import and run directly
            from standalone_discord_bot import main as run_bot
            run_bot()
        except ImportError:
            # If that fails, try completely isolated bot
            logger.warning("Could not import standalone_discord_bot, trying completely_isolated_bot")
            try:
                from completely_isolated_bot import main as run_isolated_bot
                run_isolated_bot()
            except ImportError:
                # If all imports fail, run as subprocess
                logger.warning("Could not import bot modules directly, trying subprocess")
                subprocess.run(["python", "standalone_discord_bot.py"], check=True)
    except Exception as e:
        logger.critical(f"Failed to start Discord bot: {e}")
        import traceback
        logger.critical(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()