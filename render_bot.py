"""
Special entry point for Render.com Discord bot worker service.
This file ensures that the Discord bot runs correctly in a worker dyno.
"""

import os
import time
import subprocess
import sys
import logging
import traceback

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def check_env_vars():
    """Check for required environment variables"""
    required_vars = ["DISCORD_TOKEN", "DATABASE_URL"]
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        logging.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    return True

def start_bot_directly():
    """Run the bot code in the current process"""
    try:
        logging.info("Starting Discord bot in the current process...")
        import discord_main
        discord_main.main()
        return True
    except Exception as e:
        logging.error(f"Error in bot process: {e}")
        logging.error(traceback.format_exc())
        return False

def start_bot_subprocess():
    """Run the bot as a subprocess and monitor it"""
    cmd = [sys.executable, "discord_main.py"]
    logging.info(f"Starting Discord bot as subprocess: {' '.join(cmd)}")
    
    try:
        # Run the bot in a separate process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor the process output
        if process.stdout:
            for line in process.stdout:
                print(line, end="")
        
        # Check if process terminated
        process.wait()
        return_code = process.returncode
        
        if return_code != 0:
            logging.error(f"Bot process exited with code {return_code}")
            return False
            
    except Exception as e:
        logging.error(f"Error managing bot subprocess: {e}")
        return False
    
    return True

def main():
    """Main entry point for Render.com"""
    logging.info("Starting Discord bot worker service on Render.com")
    
    if not check_env_vars():
        logging.critical("Missing environment variables. Bot cannot start.")
        sys.exit(1)
    
    # Try to run the bot directly first
    success = start_bot_directly()
    
    # If direct start fails, try running as subprocess with monitoring
    if not success:
        logging.warning("Direct start failed, trying subprocess method...")
        success = start_bot_subprocess()
    
    if not success:
        logging.critical("All start methods failed. Exiting...")
        sys.exit(1)

if __name__ == "__main__":
    main()