#!/usr/bin/env python3
"""
Isolated Discord Bot Runner

This script is a completely self-contained Discord bot that imports no modules
from the project. It's designed to run in the discord_bot workflow without
any conflicts with the web server.
"""

import os
import sys
import logging
import random
import string
import subprocess
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("isolated_bot")

print("="*80)
print("ISOLATED DISCORD BOT RUNNER")
print("This script avoids any imports from other project modules")
print("="*80)

# Try to load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
except ImportError:
    logger.warning("dotenv not installed, skipping .env loading")

# Check for Discord token
DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
if not DISCORD_TOKEN:
    logger.critical("DISCORD_TOKEN not found in environment variables")
    logger.critical("Please add your Discord bot token to the Secrets tab or .env file")
    sys.exit(1)

# Simple HTTP handler for port binding
class SimpleHandler(BaseHTTPRequestHandler):
    """Simple HTTP request handler for port binding"""
    
    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        response = """
        <html>
            <head>
                <title>Discord Bot Status</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 15px; background-color: #d4edda; border-radius: 5px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Discord Bot Status</h1>
                    <div class="status">
                        <p>Discord Bot is running on port 9000</p>
                        <p>This is a simple status page for the bot's HTTP server.</p>
                        <p>The bot is running in isolated mode.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        self.wfile.write(response.encode())
    
    def log_message(self, format, *args):
        """Override logging to use our logger"""
        logger.info(f"HTTP: {self.address_string()} - {format % args}")

def start_http_server(port=9000):
    """Start a minimal HTTP server for port binding"""
    try:
        server = HTTPServer(('0.0.0.0', port), SimpleHandler)
        logger.info(f"Starting HTTP server on port {port}")
        
        # Start in a separate thread so it doesn't block
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        logger.info("HTTP server started successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to start HTTP server on port {port}: {e}")
        return False

def main():
    """Main function to run the bot"""
    
    # Set environment variables to avoid conflicts
    os.environ["PORT"] = "9000"
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["BOT_ONLY_MODE"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    
    # Start the HTTP server first
    http_started = start_http_server(9000)
    if not http_started:
        # Try alternative port
        http_started = start_http_server(8080)
    
    # Run the standalone Discord bot directly
    try:
        logger.info("Starting standalone Discord bot...")
        subprocess.run([sys.executable, "standalone_discord_bot.py"], check=True)
    except Exception as e:
        logger.critical(f"Failed to start Discord bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()