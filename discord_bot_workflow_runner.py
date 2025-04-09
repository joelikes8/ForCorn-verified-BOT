#!/usr/bin/env python3
"""
Discord Bot Workflow Runner

This script explicitly runs the Discord bot in workflow mode.
It's designed specifically to be used in the 'discord_bot' 
workflow in the .replit configuration.

The script sets appropriate environment variables and
runs the standalone bot to avoid port conflicts with the web server.
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
logger = logging.getLogger("workflow_runner")

def main():
    """Main entry point for the Discord bot workflow"""
    # Set environment variables for bot-only mode
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    
    # Set a different port for the HTTP server to avoid conflicts with the web application
    if not os.environ.get("PORT"):
        os.environ["PORT"] = "9000"
    
    # Print status message
    logger.info("Starting Discord bot in workflow mode...")
    
    try:
        # Import the standalone bot module
        import standalone_discord_bot
        standalone_discord_bot.main()
    except Exception as e:
        logger.error(f"Error running bot in workflow mode: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()