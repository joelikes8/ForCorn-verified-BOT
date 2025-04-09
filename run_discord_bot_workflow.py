#!/usr/bin/env python3
"""
Discord Bot Workflow Script

This script is specifically designed to run in the 'discord_bot' workflow
and start only the Discord bot component without a web application.
It explicitly sets the port to 9000 to avoid conflicts with the web server.
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
logger = logging.getLogger("discord_bot_workflow")

def main():
    """Main entry point for the Discord bot workflow"""
    # Set environment variables for bot-only mode
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    os.environ["PORT"] = "9000"  # Set explicit port to avoid conflicts
    
    logger.info("Starting Discord bot in dedicated workflow with port 9000...")
    
    try:
        # Import and run the standalone bot
        import standalone_discord_bot
        standalone_discord_bot.main()
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()