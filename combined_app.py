import os
import sys
import threading
import subprocess
import logging
from webapp import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def start_bot():
    """Start the Discord bot as a separate process"""
    try:
        logger.info("Starting Discord bot...")
        # Get the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Full path to main.py
        main_py_path = os.path.join(current_dir, 'main.py')
        
        # Check if main.py exists
        if not os.path.exists(main_py_path):
            logger.error(f"main.py not found at {main_py_path}")
            return
            
        # First try python3, then python if that fails
        try:
            bot_process = subprocess.Popen(['python3', main_py_path], 
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          text=True)
        except FileNotFoundError:
            logger.info("python3 command not found, trying python...")
            bot_process = subprocess.Popen(['python', main_py_path], 
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.STDOUT,
                                          text=True)
        
        # Log bot output
        logger.info("Bot started, listening for output...")
        for line in bot_process.stdout:
            logger.info(f"BOT: {line.strip()}")
            
        # If we get here, the process has ended
        exit_code = bot_process.wait()
        logger.info(f"Bot process exited with code {exit_code}")
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    # Start the bot in a separate thread if environment variable is set
    if os.environ.get("START_BOT", "true").lower() == "true":
        logger.info("START_BOT is set to true, starting bot thread")
        bot_thread = threading.Thread(target=start_bot)
        bot_thread.daemon = True
        bot_thread.start()
        logger.info("Bot thread started")
    else:
        logger.info("START_BOT is not true, skipping bot startup")

    # Start the web app
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting web server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)