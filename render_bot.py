import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Render.com"""
    try:
        logger.info("Starting Discord bot...")
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Full path to main.py
        main_py_path = os.path.join(current_dir, 'main.py')
        
        # Check if main.py exists
        if not os.path.exists(main_py_path):
            logger.error(f"main.py not found at {main_py_path}")
            sys.exit(1)
        
        # Use the system's Python interpreter to run main.py
        logger.info(f"Executing: python {main_py_path}")
        
        # Execute the bot directly - this process will replace the current one
        os.execvp('python', ['python', main_py_path])
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("render_bot.py starting...")
    main()