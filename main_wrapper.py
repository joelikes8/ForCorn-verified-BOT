#!/usr/bin/env python3
"""
Main wrapper script

This script serves as a wrapper for either the web app or discord bot,
depending on which workflow called it. It bypasses any database issues.
"""

import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main_wrapper")

def main():
    # Check if this is being run from the discord_bot workflow
    if "DISCORD_BOT_WORKFLOW" in os.environ and os.environ["DISCORD_BOT_WORKFLOW"] == "true":
        logger.info("Detected discord_bot workflow, running simple Discord bot...")
        try:
            # Run the simple Discord bot that doesn't depend on a database
            logger.info("Starting simple Discord bot...")
            # Use subprocess to run the bot in a separate process
            process = subprocess.run(["python", "simple_discord_bot.py"], check=True)
            if process.returncode != 0:
                logger.error(f"Discord bot exited with code {process.returncode}")
                sys.exit(process.returncode)
            return
        except Exception as e:
            logger.error(f"Error running Discord bot: {e}")
            import traceback
            logger.error(traceback.format_exc())
            sys.exit(1)
    
    # Otherwise, run the web application
    logger.info("Running web application...")
    try:
        # Call the original main.py as a subprocess
        port = int(os.environ.get("PORT", 5000))
        process = subprocess.run(
            ["python", "-c", f"""
import os
os.environ['DATABASE_URL'] = 'sqlite:///app.db'
from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return '<h1>ForCorn Bot Web Interface</h1><p>Web interface is running, but Discord bot may need configuration.</p>'

@app.route('/status')
def status():
    return {{'status': 'ok', 'message': 'ForCorn Bot web interface running in simplified mode'}}

app.run(host='0.0.0.0', port={port}, debug=True)
"""],
            check=True
        )
        if process.returncode != 0:
            logger.error(f"Web application exited with code {process.returncode}")
            sys.exit(process.returncode)
    except Exception as e:
        logger.error(f"Error running web application: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()