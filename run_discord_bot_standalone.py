#!/usr/bin/env python3
"""
Dedicated Discord Bot Runner

This script is specifically designed to run the Discord bot in a standalone manner
with no web application interference. It uses environment variables to ensure
proper isolation and sets specific port bindings to avoid conflicts.
"""

import os
import sys
import subprocess
import logging
import signal
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("discord_bot_launcher")

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    logger.info("Received signal to terminate")
    sys.exit(0)

# Register signal handlers
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def is_process_running(pid):
    """Check if a process with the given PID is running"""
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False

def main():
    """Main entry point"""
    logger.info("Starting Discord bot standalone runner")
    
    # Set environment variables to ensure Discord bot mode
    env = os.environ.copy()
    env["DISCORD_BOT_WORKFLOW"] = "true"
    env["NO_WEB_SERVER"] = "true"
    env["BOT_ONLY_MODE"] = "true"
    env["PORT"] = "9000"  # Use port 9000 for bot's minimal HTTP server
    
    # Choose which bot script to run
    if os.path.exists("discord_bot_only_run.py"):
        bot_script = "discord_bot_only_run.py"
    elif os.path.exists("standalone_discord_bot.py"):
        bot_script = "standalone_discord_bot.py"
    else:
        bot_script = "final_discord_bot.py"
    
    logger.info(f"Selected bot script: {bot_script}")
    
    # Start the bot
    try:
        logger.info(f"Launching Discord bot using: {bot_script}")
        process = subprocess.Popen(
            [sys.executable, bot_script],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )
        
        logger.info(f"Bot process started with PID: {process.pid}")
        
        # Verify stdout is correctly set
        if process.stdout is None:
            logger.error("Failed to capture bot process output")
            return 1
        
        # Monitor the process and log its output
        while True:
            # Check if process is still running
            if not is_process_running(process.pid):
                logger.error("Bot process has died unexpectedly")
                return 1
            
            # Read output line by line (with None check)
            if process.stdout:
                output = process.stdout.readline()
                if output:
                    print(output.decode().strip())
            
            # Sleep a bit to avoid high CPU usage
            time.sleep(0.1)
    
    except Exception as e:
        logger.error(f"Error running Discord bot: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())