#!/usr/bin/env python3
"""
Discord bot runner script (no web interface)

This script runs only the Discord bot without any web interface.
It's designed to be used in a dedicated workflow for the bot.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bot_only")

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Check for Discord token
if not os.environ.get("DISCORD_TOKEN"):
    logger.critical("DISCORD_TOKEN environment variable is missing")
    sys.exit(1)

# Import the Discord bot main function
try:
    from discord_main import main
    
    # Run the Discord bot
    logger.info("Starting Discord bot...")
    main()
except ImportError as e:
    logger.critical(f"Could not import from discord_main.py: {e}")
    sys.exit(1)
except Exception as e:
    logger.critical(f"Error running Discord bot: {e}")
    import traceback
    logger.critical(traceback.format_exc())
    sys.exit(1)