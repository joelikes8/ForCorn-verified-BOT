#!/usr/bin/env python3
"""
Main Discord Bot Entry Point for Workflow

This script is specifically designed to be used as the entry point for the 'discord_bot' workflow.
It handles port conflicts by explicitly setting PORT=9000 and ensures the bot runs in isolation.
"""

import os
import sys
import logging

# Set environment variables to prevent conflicts
os.environ["PORT"] = "9000"
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot_main")

# Load the standalone bot directly
logger.info("Starting standalone Discord bot...")

try:
    # Import and run the standalone bot module directly
    from standalone_discord_bot import main as run_bot
    
    # Run the bot
    run_bot()
except Exception as e:
    logger.critical(f"Failed to start bot: {e}")
    import traceback
    logger.critical(traceback.format_exc())
    sys.exit(1)