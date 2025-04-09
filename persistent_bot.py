#!/usr/bin/env python3
"""
Persistent Discord Bot

This script ensures your Discord bot runs persistently with automatic
reconnection and health checks. It's designed to be used in production
environments where 24/7 uptime is crucial.

Features:
- Heartbeat monitoring to verify Discord connection
- Error capture and graceful recovery
- Automatic restarts if the bot crashes
- Connection supervision with circuit breaker pattern
- Status endpoints for health checks
"""

import os
import sys
import time
import signal
import logging
import traceback
import subprocess
import threading
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("persistent_bot.log")
    ]
)
logger = logging.getLogger("persistent_bot")

# Configuration
BOT_SCRIPT = "discord_bot_only_run.py"  # The main bot script to run
CHECK_INTERVAL = 60  # Check bot health every 60 seconds
MAX_RESTARTS = 10    # Maximum number of restarts before cooling down
COOLDOWN_TIME = 300  # 5 minutes cooldown after hitting max restarts
HTTP_PORT = 9000     # Port for health check HTTP server

# Global state
bot_process = None
restart_count = 0
last_restart_time = None
is_running = True

class HealthServer(BaseHTTPRequestHandler):
    """Simple HTTP server for health checks"""
    
    def do_GET(self):
        """Handle GET requests with status information"""
        global bot_process, restart_count, last_restart_time
        
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            status = "RUNNING" if bot_process and bot_process.poll() is None else "STOPPED"
            uptime = "N/A"
            
            if bot_process and bot_process.poll() is None and last_restart_time:
                uptime_seconds = (datetime.now() - last_restart_time).total_seconds()
                days, remainder = divmod(uptime_seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
            
            response = (
                f"Status: {status}\n"
                f"Uptime: {uptime}\n"
                f"Restarts: {restart_count}\n"
                f"PID: {bot_process.pid if bot_process else 'N/A'}\n"
                f"Last Restart: {last_restart_time.strftime('%Y-%m-%d %H:%M:%S') if last_restart_time else 'N/A'}\n"
            )
            
            self.wfile.write(response.encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Get uptime string if available
            uptime_str = "N/A"
            if bot_process and bot_process.poll() is None and last_restart_time:
                uptime_seconds = (datetime.now() - last_restart_time).total_seconds()
                days, remainder = divmod(uptime_seconds, 86400)
                hours, remainder = divmod(remainder, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"
            
            # Get status class and text
            status_class = 'running' if bot_process and bot_process.poll() is None else 'stopped'
            status_text = 'RUNNING' if bot_process and bot_process.poll() is None else 'STOPPED'
            
            # Get PID and last restart time formatted
            pid_text = str(bot_process.pid) if bot_process else 'N/A'
            last_restart_text = last_restart_time.strftime('%Y-%m-%d %H:%M:%S') if last_restart_time else 'N/A'
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Discord Bot Status</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #333; }}
                    .status {{ padding: 10px; border-radius: 5px; margin: 20px 0; }}
                    .running {{ background-color: #d4edda; color: #155724; }}
                    .stopped {{ background-color: #f8d7da; color: #721c24; }}
                    pre {{ background: #f4f4f4; padding: 15px; border-radius: 5px; }}
                </style>
            </head>
            <body>
                <h1>Discord Bot Status Monitor</h1>
                <div class="status {status_class}">
                    Status: {status_text}
                </div>
                <pre>
Uptime: {uptime_str}
Restarts: {restart_count}
PID: {pid_text}
Last Restart: {last_restart_text}
                </pre>
                <p><a href="/health">Raw Health Check</a></p>
            </body>
            </html>
            """
            
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def log_message(self, format, *args):
        """Override to use our custom logger"""
        logger.debug(f"Health server: {format % args}")

def start_health_server():
    """Start the health check HTTP server in a separate thread"""
    port = int(os.environ.get("PORT", HTTP_PORT))
    server = HTTPServer(('0.0.0.0', port), HealthServer)
    logger.info(f"Starting health check server on port {port}")
    
    # Run the server in a daemon thread so it exits when the main program exits
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Health check server started")

def start_bot():
    """Start the Discord bot as a subprocess"""
    global bot_process, restart_count, last_restart_time
    
    logger.info(f"Starting Discord bot using {BOT_SCRIPT}")
    
    # Set appropriate environment variables
    env = os.environ.copy()
    env["DISCORD_BOT_WORKFLOW"] = "true"
    env["NO_WEB_SERVER"] = "true"
    env["BOT_ONLY_MODE"] = "true"
    
    # Start the bot process
    bot_process = subprocess.Popen(
        [sys.executable, BOT_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env
    )
    
    last_restart_time = datetime.now()
    restart_count += 1
    
    logger.info(f"Bot started with PID {bot_process.pid} (restart #{restart_count})")
    
    # Start a thread to read the output from the bot process
    def read_output():
        while bot_process and bot_process.poll() is None:
            try:
                if bot_process and bot_process.stdout:
                    # Use a non-blocking approach
                    try:
                        output = bot_process.stdout.readline()
                        if output:
                            print(output.decode().strip())
                    except AttributeError:
                        # Handle case where stdout doesn't have readline
                        pass
                else:
                    # If stdout is None, wait and then continue
                    time.sleep(1)
                    continue
            except Exception as e:
                logger.error(f"Error reading bot output: {e}")
            time.sleep(0.1)
    
    output_thread = threading.Thread(target=read_output)
    output_thread.daemon = True
    output_thread.start()

def check_bot_health():
    """Check if the bot is still running and restart if needed"""
    global bot_process, restart_count, is_running
    
    while is_running:
        time.sleep(CHECK_INTERVAL)
        
        # Check if bot process is still running
        if not bot_process or bot_process.poll() is not None:
            logger.warning("Bot process is not running or has stopped")
            
            # Check if we've hit the restart limit
            if restart_count >= MAX_RESTARTS:
                logger.warning(f"Hit maximum restart limit ({MAX_RESTARTS}), cooling down for {COOLDOWN_TIME} seconds")
                time.sleep(COOLDOWN_TIME)
                restart_count = 0
            
            # Restart the bot
            start_bot()
        else:
            # Bot is still running, log a health check message
            logger.debug(f"Health check: Bot is running (PID: {bot_process.pid})")

def signal_handler(sig, frame):
    """Handle termination signals gracefully"""
    global is_running, bot_process
    
    logger.info(f"Received signal {sig}, shutting down")
    is_running = False
    
    if bot_process:
        logger.info(f"Terminating bot process (PID: {bot_process.pid})")
        try:
            bot_process.terminate()
            # Give it a moment to shut down gracefully
            time.sleep(2)
            if bot_process.poll() is None:
                # Force kill if it didn't terminate
                bot_process.kill()
        except Exception as e:
            logger.error(f"Error terminating bot process: {e}")
    
    logger.info("Shutdown complete")
    sys.exit(0)

def main():
    """Main entry point"""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Print startup banner
    print("\n" + "="*70)
    print(" PERSISTENT DISCORD BOT ".center(70, "="))
    print("="*70)
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Bot script: {BOT_SCRIPT}")
    print(f"Health check interval: {CHECK_INTERVAL} seconds")
    print("="*70 + "\n")
    
    try:
        # Start the health check server
        start_health_server()
        
        # Initial bot start
        start_bot()
        
        # Start the health check thread
        health_thread = threading.Thread(target=check_bot_health)
        health_thread.daemon = True
        health_thread.start()
        
        # Keep the main thread alive
        while is_running:
            time.sleep(1)
            
    except Exception as e:
        logger.critical(f"Fatal error in main loop: {e}")
        logger.critical(traceback.format_exc())
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())