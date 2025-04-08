#!/usr/bin/env python3
"""
This is a simple script that directly imports and runs the standalone_discord_bot
It avoids all the complexity of the main.py to ensure the bot runs correctly
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
logger = logging.getLogger("bot_runner")

# Set environment variables to ensure we run in bot-only mode
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"

logger.info("Starting standalone Discord bot...")

# Run the standalone bot
try:
    import standalone_discord_bot
    standalone_discord_bot.main()
except Exception as e:
    logger.error(f"Error running bot: {e}")
    sys.exit(1)