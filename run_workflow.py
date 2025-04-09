#!/usr/bin/env python3
"""
Discord Bot Workflow Runner

This script is designed to be used by the Replit workflow system to run the Discord bot.
It detects if it should run the bot or the web server based on the workflow name.
"""

import os
import sys
import logging
import importlib.util

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("workflow_runner")

def is_workflow(name):
    """Check if we're running in a specific workflow"""
    return os.environ.get("REPLIT_WORKFLOW") == name

def main():
    """Main function to detect and run the correct component"""
    # Detect workflow or use environment variable
    running_discord_bot = is_workflow("discord_bot") or os.environ.get("DISCORD_BOT_WORKFLOW")
    
    # Log what we're doing
    if running_discord_bot:
        logger.info("Detected discord_bot workflow - starting Discord bot...")
        # Set environment variables for bot mode
        os.environ["DISCORD_BOT_WORKFLOW"] = "true"
        os.environ["BOT_ONLY_MODE"] = "true"
        os.environ["NO_WEB_SERVER"] = "true"
        
        # Run our specialized bot starter
        try:
            # First try importing and running
            if os.path.exists("discord_bot_main.py"):
                logger.info("Starting bot using discord_bot_main.py...")
                spec = importlib.util.spec_from_file_location("discord_bot_main", "discord_bot_main.py")
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                sys.exit(0)
        except Exception as e:
            logger.warning(f"Failed to run discord_bot_main.py: {e}")
        
        # Fallback method: try our bot wrapper
        try:
            os.execv(sys.executable, [sys.executable, 'discord_bot_wrapper.py'])
        except Exception as e:
            logger.error(f"Failed to execute discord_bot_wrapper.py: {e}")
            
            # Last resort: try running start_discord_bot.py
            try:
                os.execv(sys.executable, [sys.executable, 'start_discord_bot.py'])
            except Exception as e2:
                logger.critical(f"All methods failed: {e2}")
                sys.exit(1)
    else:
        # We're in the web workflow or no specific workflow, run the web server
        logger.info("Starting web application...")
        try:
            # Use execv to avoid leaving this process running
            os.execv(sys.executable, [sys.executable, 'main.py'])
        except Exception as e:
            logger.critical(f"Failed to start web application: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()