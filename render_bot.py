import os
import sys
import subprocess
import logging
import time
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
try:
    load_dotenv()
    print("Loaded environment from .env file")
except Exception as e:
    print(f"Note: Could not load .env file: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def check_env_vars():
    """Check for required environment variables"""
    required_vars = ['DISCORD_TOKEN']
    missing = [var for var in required_vars if not os.environ.get(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set these variables in your Render.com dashboard or .env file")
        return False
    return True

def start_bot_directly():
    """Run the bot code in the current process"""
    try:
        logger.info("Starting Discord bot directly in current process...")
        # This will import and run the bot in the current process
        import main
        
        # This will only be reached if main.py exits normally
        logger.info("Bot has stopped.")
        return 0
    except ImportError as e:
        logger.error(f"Failed to import main.py: {e}")
        return 1
    except Exception as e:
        logger.error(f"Error running bot directly: {e}")
        return 1

def start_bot_subprocess():
    """Run the bot as a subprocess and monitor it"""
    try:
        logger.info("Starting Discord bot as subprocess...")
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Full path to main.py
        main_py_path = os.path.join(current_dir, 'main.py')
        
        # Check if main.py exists
        if not os.path.exists(main_py_path):
            logger.error(f"main.py not found at {main_py_path}")
            return 1
        
        # Start the bot as a subprocess
        cmd = [sys.executable, main_py_path]
        logger.info(f"Executing: {' '.join(cmd)}")
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy()
        )
        
        # Monitor the process
        while True:
            if process.poll() is not None:
                # Process has terminated
                return_code = process.returncode
                logger.info(f"Bot process exited with code {return_code}")
                return return_code
                
            # Read output line by line
            line = process.stdout.readline()
            if line:
                print(line.rstrip())
            else:
                time.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Error starting bot subprocess: {e}")
        return 1

def main():
    """Main entry point for Render.com"""
    logger.info("render_bot.py starting...")
    
    # Print Python version and environment info
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Current directory: {os.getcwd()}")
    
    # Check for required environment variables
    if not check_env_vars():
        return 1
    
    # Try two different approaches
    try:
        # First approach: Run directly in the same process
        logger.info("Attempting to start bot directly...")
        return_code = start_bot_directly()
        
        if return_code != 0:
            # If that fails, try the subprocess approach
            logger.info("Direct approach failed, trying subprocess...")
            return_code = start_bot_subprocess()
        
        return return_code
        
    except Exception as e:
        logger.error(f"Bot startup failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)