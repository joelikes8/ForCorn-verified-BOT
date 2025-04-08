import os
import sys
import json
import threading
import subprocess
import logging
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Configure database
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    logger.warning("DATABASE_URL environment variable not set. Using SQLite instead.")
    database_url = "sqlite:///bot.db"

# Handle Render.com's PostgreSQL URL format
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize app with extensions
db.init_app(app)

# Create tables
with app.app_context():
    try:
        # Import models here to avoid circular imports
        import models
        db.create_all()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")

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
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

# Create necessary templates directory and basic template if it doesn't exist
os.makedirs('templates', exist_ok=True)

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

# Handle startup automatically
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