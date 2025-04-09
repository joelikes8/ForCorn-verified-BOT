#!/usr/bin/env python3
"""
Replit Discord Bot Runner

This is a specialized script for running the Discord bot directly in Replit.
It's designed to be called from the discord_bot workflow and ensures the web app
is completely bypassed.
"""

import os
import sys
import time
import signal
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("replit_runner")

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info("Received signal %s, shutting down...", sig)
    sys.exit(0)

def kill_existing_processes():
    """Kill any existing Python processes to avoid conflicts"""
    logger.info("Killing any existing Python processes...")
    try:
        subprocess.run(["pkill", "-f", "python"], check=False)
        subprocess.run(["pkill", "-f", "gunicorn"], check=False)
        subprocess.run(["pkill", "-f", "flask"], check=False)
        time.sleep(1)
    except Exception as e:
        logger.warning("Error killing processes: %s", e)

def run_discord_bot():
    """Run the Discord bot with all necessary environment variables"""
    # Set environment variables
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    os.environ["PORT"] = "9000"
    
    # Print a clear message
    logger.info("=" * 80)
    logger.info("REPLIT DISCORD BOT RUNNER")
    logger.info("This script runs ONLY the Discord bot, completely bypassing the web app")
    logger.info("=" * 80)
    
    # Make sure data directory exists
    os.makedirs("data", exist_ok=True)
    
    # Run the Discord bot directly
    try:
        logger.info("Starting the standalone Discord bot...")
        bot_script = "final_discord_bot.py"
        if not os.path.exists(bot_script):
            bot_script = "standalone_discord_bot.py"
        
        logger.info("Using bot script: %s", bot_script)
        os.execv(sys.executable, [sys.executable, bot_script])
    except Exception as e:
        logger.critical("Failed to start the Discord bot: %s", e)
        sys.exit(1)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Kill existing processes first
    kill_existing_processes()
    
    # Run the Discord bot
    run_discord_bot()