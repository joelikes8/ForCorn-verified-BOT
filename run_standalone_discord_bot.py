#!/usr/bin/env python3
"""
Standalone Discord Bot Runner

This script ONLY runs the Discord bot and has no dependencies on any web-related code.
It completely bypasses any imports from the main app.
"""

import os
import logging
import sys

# Set environment variables to ensure bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true" 
os.environ["NO_WEB_SERVER"] = "true"
os.environ["PORT"] = "9000"  # Use port 9000 to avoid conflicts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("discord_bot_runner")

logger.info("Starting standalone Discord bot")

try:
    # Directly import and run the standalone bot
    # No other imports should be done to avoid conflicts
    import standalone_discord_bot
    
    # Call the main function
    if hasattr(standalone_discord_bot, 'main'):
        standalone_discord_bot.main()
    else:
        logger.error("No main function found in standalone_discord_bot.py!")
        sys.exit(1)
except Exception as e:
    logger.critical(f"Failed to start Discord bot: {e}")
    import traceback
    logger.critical(traceback.format_exc())
    sys.exit(1)