"""
Web application for ForCorn Discord Bot

This is a simplified web interface for the ForCorn Discord Bot.
It provides basic status information and configuration options.
"""

import os
import logging
import sys
from flask import Flask, render_template, jsonify
from sqlalchemy.orm import DeclarativeBase
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("webapp")

# Load environment variables
load_dotenv()

# Create base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Create and configure Flask app with SQLAlchemy
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Try to use DATABASE_URL, but fall back to SQLite if not available
database_url = os.environ.get("DATABASE_URL")
if not database_url:
    database_url = "sqlite:///app.db"
    logger.warning(f"DATABASE_URL not found, using SQLite: {database_url}")

# Configure Flask-SQLAlchemy
app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Create database instance
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import models and initialize database
with app.app_context():
    try:
        # Import models if available
        try:
            import models
            logger.info("Models imported successfully")
        except ImportError:
            logger.warning("Could not import models, database functionality may be limited")
        
        # Create tables
        db.create_all()
        logger.info("Database tables created")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        logger.error("Web application will run with limited functionality")

# Routes
@app.route('/')
def index():
    """Return the main index page"""
    return render_template('index.html')

@app.route('/status')
def status():
    """Return the status of the application"""
    return jsonify({
        "status": "ok",
        "message": "ForCorn Bot web interface is running",
        "version": "1.0.0",
        "database_available": db is not None,
        "database_url": database_url.replace("://", "://<redacted>:<redacted>@") if "://" in database_url else database_url
    })

@app.route('/api/status')
def api_status():
    """Return the status of the bot for the API"""
    # Check if Discord bot is running
    try:
        import psutil
        bot_running = False
        for process in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = ' '.join(process.info['cmdline'] or []).lower()
            if 'discord' in cmdline and 'bot' in cmdline:
                bot_running = True
                break
        
        return jsonify({
            "status": "online" if bot_running else "offline",
            "message": "Bot is operational" if bot_running else "Bot is not running",
            "server_count": "2+",  # Placeholder
            "using_database": "postgresql" in database_url.lower()
        })
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        return jsonify({
            "status": "offline",
            "message": f"Could not check bot status: {str(e)}"
        })

@app.route('/start-bot')
def start_bot():
    """Start the Discord bot as a separate process"""
    try:
        logger.info("Starting Discord bot...")
        import subprocess
        process = subprocess.Popen(["python", "simple_discord_bot.py"])
        logger.info(f"Started Discord bot (PID: {process.pid})")
        return jsonify({
            "status": "ok",
            "message": "Discord bot started",
            "pid": process.pid
        })
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        return jsonify({
            "status": "error",
            "message": f"Error starting bot: {str(e)}"
        }), 500

# Run the app if executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
