"""
Discord Bot Wrapper Script

This script is a wrapper that runs the standalone Discord bot.
It's needed because the Replit workflow system can't be modified directly.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_wrapper")

def main():
    """Run the standalone Discord bot"""
    logger.info("Starting Discord bot through wrapper...")
    
    # Set environment variable to indicate this is the Discord bot workflow
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    
    # Run the standalone bot
    try:
        logger.info("Executing standalone_discord_bot.py")
        return subprocess.call([sys.executable, "standalone_discord_bot.py"])
    except Exception as e:
        logger.error(f"Error executing standalone bot: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())