"""
Special entry point for Render.com Discord bot worker service.
This file ensures that the Discord bot runs correctly in a worker dyno.
"""

import os
import sys
import subprocess
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("render_bot")

def check_env_vars():
    """Check for required environment variables"""
    required_vars = ["DISCORD_TOKEN"]
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        logger.error("Bot cannot start without these variables set.")
        return False
    return True

def start_bot_directly():
    """Run the bot code in the current process"""
    logger.info("Starting Discord bot directly...")
    try:
        from discord_bot_workflow import main
        main()
    except Exception as e:
        logger.error(f"Error running Discord bot directly: {e}")
        return False
    return True

def start_bot_subprocess():
    """Run the bot as a subprocess and monitor it"""
    logger.info("Starting Discord bot as subprocess...")
    
    while True:
        try:
            # Run process and capture output
            result = subprocess.run(
                [sys.executable, "discord_bot_workflow.py"],
                check=False,
                capture_output=True,
                text=True
            )
            
            # Log the output
            if result.stdout:
                logger.info("Bot output:")
                for line in result.stdout.splitlines():
                    logger.info(line)
            
            # Log any errors
            if result.stderr:
                logger.error("Bot errors:")
                for line in result.stderr.splitlines():
                    logger.error(line)
            
            # Check exit code
            if result.returncode != 0:
                logger.error(f"Bot process exited with code {result.returncode}. Restarting in 10 seconds...")
                time.sleep(10)
            else:
                logger.info("Bot process exited cleanly.")
                break
                
        except Exception as e:
            logger.error(f"Error running subprocess: {e}")
            logger.error("Restarting in 10 seconds...")
            time.sleep(10)

def main():
    """Main entry point for Render.com"""
    logger.info("=== ForCorn Discord Bot - Render.com Worker ===")
    
    if not check_env_vars():
        sys.exit(1)
    
    logger.info("Environment variables verified.")
    
    # Try to start the bot directly first
    success = start_bot_directly()
    
    # If direct start fails, try subprocess method
    if not success:
        logger.info("Direct start failed, switching to subprocess method.")
        start_bot_subprocess()

if __name__ == "__main__":
    main()