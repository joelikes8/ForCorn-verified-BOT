#!/usr/bin/env python3
"""
Specialized Discord bot runner for Replit

This script runs only the Discord bot component without starting 
the Flask web application. This allows the bot to be run in a 
separate workflow from the web interface.
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
logger = logging.getLogger("discord_bot_runner")

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file: {e}")

# Check if Discord token is available
if not os.environ.get("DISCORD_TOKEN"):
    logger.error("DISCORD_TOKEN not found in environment variables")
    logger.error("Please make sure you have a valid Discord bot token in your .env file")
    sys.exit(1)

# Make sure we don't try to use Flask on this process - just in case
# This is to prevent any attempts to start a web server in this process
os.environ["START_BOT"] = "true"
os.environ["DISABLE_WEB"] = "true"

# Import the main function from discord_main.py
try:
    # Directly import the main function to avoid any potential Flask initializations
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