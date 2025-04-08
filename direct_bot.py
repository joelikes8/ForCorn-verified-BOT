#!/usr/bin/env python3
"""
Direct Bot Launcher

This script imports and runs the completely isolated bot.
It avoids any imports from the main project to prevent conflicts.
"""

import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("direct_bot")

logger.info("Starting direct bot launcher...")

# Direct import to the isolated bot
try:
    from completely_isolated_bot import main as run_bot
    logger.info("Successfully imported isolated bot")
    run_bot()
except Exception as e:
    logger.error(f"Failed to run isolated bot: {e}")
    import traceback
    logger.error(traceback.format_exc())
    sys.exit(1)