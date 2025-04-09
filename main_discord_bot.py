"""
Main Discord Bot Entry Point for Workflow

This script is specifically designed to be used as the entry point for the 'discord_bot' workflow.
It handles port conflicts by explicitly setting PORT=9000 and ensures the bot runs in isolation.
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
logger = logging.getLogger("main_discord_bot")

# Set critical environment variables
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["PORT"] = "9000"  # Explicit port to avoid conflicts

logger.info("=" * 50)
logger.info("STARTING DISCORD BOT IN DEDICATED WORKFLOW (PORT 9000)")
logger.info("=" * 50)

try:
    # Import and run the standalone bot
    import standalone_discord_bot
    standalone_discord_bot.main()
except Exception as e:
    logger.error(f"Error running Discord bot: {e}")
    
    # Try fallback options
    try:
        logger.info("Trying simple bot as fallback...")
        import simple_discord_bot
        simple_discord_bot.run_bot()
    except Exception as e2:
        logger.critical(f"All bot startup methods failed: {e2}")
        sys.exit(1)