import os
import json
import threading
import subprocess
import sys
import logging
import time
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except Exception as e:
    logger.warning(f"Could not load .env file (this is normal in production): {e}")

# System information debug logging
logger.info(f"Python version: {sys.version}")
logger.info(f"Current working directory: {os.getcwd()}")
try:
    files = os.listdir('.')
    logger.info(f"Files in current directory: {', '.join(files)}")
except Exception as e:
    logger.error(f"Error listing directory: {e}")

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Fix for proxy headers in production environments
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    logger.warning("DATABASE_URL environment variable not set. Using SQLite instead.")
    database_url = "sqlite:///bot.db"

# Handle Render.com's PostgreSQL URL format
if database_url and database_url.startswith("postgres://"):
    logger.info("Converting postgres:// to postgresql:// for SQLAlchemy compatibility")
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

logger.info(f"Database URL configured: {database_url[:10]}***")

# Initialize app with extensions
db.init_app(app)

# Create necessary templates directory and basic template if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Check if index.html exists, and create a simple one if not
index_path = os.path.join('templates', 'index.html')
if not os.path.exists(index_path):
    logger.info("Creating default index.html template")
    with open(index_path, 'w') as f:
        f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>ForCorn Discord Bot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #7289DA;
        }
        .status-card {
            background: #f8f9fa;
            border-left: 4px solid #7289DA;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }
        .online {
            border-left-color: #43B581;
        }
        .offline {
            border-left-color: #F04747;
        }
        .feature-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .feature {
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .feature h3 {
            margin-top: 0;
            color: #7289DA;
        }
        @media (max-width: 600px) {
            .feature-list {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>ForCorn Discord Bot</h1>
        <p>A versatile Discord bot for Roblox group management and server moderation.</p>
        
        <div id="status-container" class="status-card">
            <h2>Bot Status</h2>
            <p id="status-message">Checking status...</p>
        </div>
        
        <h2>Features</h2>
        <div class="feature-list">
            <div class="feature">
                <h3>Roblox Verification</h3>
                <p>Verify Discord members with their Roblox accounts.</p>
            </div>
            <div class="feature">
                <h3>Group Ranking</h3>
                <p>Manage your Roblox group ranks directly from Discord.</p>
            </div>
            <div class="feature">
                <h3>Ticket System</h3>
                <p>Create and manage support tickets for your server.</p>
            </div>
            <div class="feature">
                <h3>Moderation Tools</h3>
                <p>Efficiently moderate your server with anti-raid protection.</p>
            </div>
        </div>
        
        <h2>Get Started</h2>
        <p>Add the bot to your server and use <code>/verify</code> to begin.</p>
    </div>
    
    <script>
        // Fetch bot status
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusContainer = document.getElementById('status-container');
                    const statusMessage = document.getElementById('status-message');
                    
                    if (data.status === 'online') {
                        statusContainer.classList.add('online');
                        statusContainer.classList.remove('offline');
                        statusMessage.textContent = `Online - Currently serving ${data.server_count || 0} servers`;
                    } else if (data.status === 'initializing') {
                        statusContainer.classList.remove('online');
                        statusContainer.classList.remove('offline');
                        statusMessage.textContent = 'Initializing - Bot is starting up...';
                        setTimeout(checkStatus, 5000);
                    } else {
                        statusContainer.classList.remove('online');
                        statusContainer.classList.add('offline');
                        statusMessage.textContent = `Offline - ${data.message || 'Bot is currently unavailable'}`;
                    }
                })
                .catch(error => {
                    console.error('Error fetching status:', error);
                    const statusContainer = document.getElementById('status-container');
                    const statusMessage = document.getElementById('status-message');
                    statusContainer.classList.remove('online');
                    statusContainer.classList.add('offline');
                    statusMessage.textContent = 'Offline - Could not connect to server';
                });
        }
        
        // Check status when page loads
        document.addEventListener('DOMContentLoaded', () => {
            checkStatus();
        });
    </script>
</body>
</html>
        """)

# Create tables
try:
    with app.app_context():
        # Import models here to avoid circular imports
        import models
        logger.info("Creating database tables")
        db.create_all()
        logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")
    # Continue - we'll let the application handle database errors

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Status route to check if the bot is online
@app.route('/api/status')
def status():
    try:
        # Import models here to avoid circular imports
        from models import Guild
        
        # Count number of servers in the database
        guild_count = Guild.query.count()
        
        if guild_count > 0 or os.path.exists('data/server_configs.json'):
            return jsonify({
                'status': 'online',
                'message': 'Bot is running',
                'server_count': guild_count,
                'using_database': True
            })
        else:
            return jsonify({
                'status': 'initializing',
                'message': 'Bot is starting up',
                'using_database': True
            })
    except Exception as e:
        logger.error(f"Error in /api/status endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# Bot process
bot_process = None

def start_bot():
    """Start the Discord bot as a separate process"""
    global bot_process
    try:
        # Start the Discord bot in a separate process
        logger.info("Starting Discord bot subprocess")
        bot_process = subprocess.Popen(
            [sys.executable, 'main.py'], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            env=os.environ.copy()
        )
        
        logger.info(f"Bot process started with PID: {bot_process.pid}")
        
        # Log bot output
        while True:
            if bot_process.poll() is not None:
                logger.info(f"Bot process exited with code: {bot_process.returncode}")
                break
                
            line = bot_process.stdout.readline()
            if line:
                logger.info(f"BOT: {line.strip()}")
            else:
                time.sleep(0.1)
                
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

# Start the bot in a separate thread if environment variable is set
if os.environ.get("START_BOT", "false").lower() == "true":
    logger.info("Starting bot in a background thread")
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Bot thread started")
else:
    logger.info("Bot not started - START_BOT environment variable is not set to 'true'")

# Environmental information route for debugging
@app.route('/debug')
def debug_info():
    """Return debug information about the environment"""
    if app.debug:
        debug_data = {
            'python_version': sys.version,
            'working_directory': os.getcwd(),
            'environment_variables': {k: '[HIDDEN]' if k.lower() in ('discord_token', 'session_secret') else v 
                                     for k, v in os.environ.items()},
            'files_in_directory': os.listdir('.'),
            'templates_directory': os.listdir('templates') if os.path.exists('templates') else 'Not found',
            'data_directory': os.listdir('data') if os.path.exists('data') else 'Not found',
            'bot_process': f"Running (PID: {bot_process.pid})" if bot_process and bot_process.poll() is None else "Not running",
            'database_configured': bool(database_url),
        }
        return jsonify(debug_data)
    else:
        return jsonify({'error': 'Debug mode is not enabled'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Print the port we're binding to - helpful for debugging
    logger.info(f"Starting server on port {port}")
    logger.info(f"Environment variables: PORT={os.environ.get('PORT')}")
    logger.info(f"Using host: 0.0.0.0 and port: {port}")
    # Ensure we're binding to 0.0.0.0 to make the app accessible
    app.run(host='0.0.0.0', port=port, debug=True)
