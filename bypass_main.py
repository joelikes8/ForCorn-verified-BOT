#!/usr/bin/env python3
"""
Completely Independent Main Script for the Discord Bot

This script imports NO modules from the web application and contains 
no dependencies on the web application code.
"""

import logging
import os
import sys

# Set environment variables to avoid any web app conflicts
os.environ["PORT"] = "9000"  # Use non-standard port
os.environ["BOT_ONLY_MODE"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["DISCORD_BOT_WORKFLOW"] = "true"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("bypass_main")

# Directly import and run the standalone bot
logger.info("Starting Discord bot without any web app imports...")

# Import the discord bot module directly
try:
    from standalone_discord_bot import main
    main()
except ImportError as e:
    logger.critical(f"Failed to import standalone_discord_bot: {e}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error running Discord bot: {e}")
    import traceback
    logger.critical(traceback.format_exc())
    sys.exit(1)