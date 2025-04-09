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
import signal
import logging
import subprocess
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot_workflow")

def main():
    """Main entry point for the Discord bot workflow"""
    # Set environment variables to ensure we're in bot mode
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    os.environ["PORT"] = "9000"  # Use a different port to avoid conflicts
    
    logger.info("Starting Discord bot in workflow mode...")
    
    # Kill any existing web server processes
    try:
        logger.info("Terminating any existing web server processes...")
        # Find and kill Flask/Gunicorn processes
        kill_cmds = [
            "pkill -f 'python.*main\.py'",
            "pkill -f 'gunicorn'",
        ]
        for cmd in kill_cmds:
            try:
                subprocess.run(cmd, shell=True, check=False)
            except Exception as e:
                logger.debug(f"Command {cmd} failed: {e}")
        
        # Wait a moment for processes to terminate
        time.sleep(1)
    except Exception as e:
        logger.warning(f"Error killing existing processes: {e}")
    
    # Run the standalone Discord bot
    try:
        logger.info("Starting Discord bot...")
        # Here we directly import and run the standalone bot
        from standalone_discord_bot import main as run_standalone_bot
        
        # This will block until the bot exits
        run_standalone_bot()
        
        logger.info("Discord bot exited")
        return 0
    except Exception as e:
        logger.error(f"Error running standalone bot: {e}", exc_info=True)
        
        # Try running as a subprocess as fallback
        try:
            logger.info("Trying to run standalone bot as subprocess...")
            if os.path.exists("standalone_discord_bot.py"):
                result = subprocess.run(["python", "standalone_discord_bot.py"], check=True)
                return result.returncode
            else:
                logger.critical("standalone_discord_bot.py not found!")
        except Exception as e2:
            logger.critical(f"Subprocess also failed: {e2}")
        
        return 1

if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    sys.exit(main())