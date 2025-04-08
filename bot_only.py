#!/usr/bin/env python3
"""
Discord bot runner script (no web interface)

This script runs only the Discord bot without any web interface.
It's designed to be used in a dedicated workflow for the bot.
"""

import os
import sys
import logging
import importlib.util
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("bot_only")

# Force bot-only environment variables
os.environ["DISCORD_BOT_WORKFLOW"] = "true"
os.environ["NO_WEB_SERVER"] = "true"
os.environ["BOT_ONLY_MODE"] = "true"

# Print conspicuous header
print("="*80)
print("DISCORD BOT ONLY MODE - NO WEB INTERFACE")
print("This script runs the standalone Discord bot with no web components")
print("="*80)

# Check if the token is available
if not os.environ.get("DISCORD_TOKEN"):
    logger.critical("DISCORD_TOKEN not found in environment variables")
    logger.critical("Please set the DISCORD_TOKEN in Secrets tab or .env file")
    sys.exit(1)

def main():
    """Main function to run the Discord bot workflow"""
    logger.info("Starting Discord bot in bot-only mode")
    
    # Run the standalone bot directly via subprocess
    # This approach avoids any module import conflicts
    try:
        subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
    except subprocess.CalledProcessError as e:
        logger.critical(f"Bot process exited with error code {e.returncode}")
        sys.exit(e.returncode)
    except Exception as e:
        logger.critical(f"Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()