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

# Try to use DATABASE_URL, but fall back to SQLite if not available or invalid
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
    "connect_args": {"connect_timeout": 10}  # Add a timeout for database connections
}

# Flag to track database connectivity
db_connected = False
models_imported = False

# Create database instance
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Import models and initialize database
with app.app_context():
    try:
        # Import models if available
        try:
            import models
            models_imported = True
            logger.info("Models imported successfully")
        except ImportError:
            logger.warning("Could not import models, database functionality may be limited")
        
        # Attempt to create tables
        db.create_all()
        logger.info("Database tables created")
        db_connected = True
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error initializing database: {error_msg}")
        
        # Store the error message for display
        app.config["DB_ERROR"] = error_msg
        
        # If PostgreSQL connection fails, try SQLite as fallback
        if "postgresql" in database_url.lower() and not os.environ.get("FORCE_POSTGRES", False):
            logger.info("Attempting to use SQLite as fallback...")
            
            # Close any existing connections
            db.session.remove()
            db.engine.dispose()
            
            # Switch to SQLite
            fallback_db_url = "sqlite:///app.db"
            app.config["SQLALCHEMY_DATABASE_URI"] = fallback_db_url
            
            # Reinitialize with SQLite
            try:
                # Don't call init_app again, just change the URI
                if models_imported:
                    try:
                        with app.app_context():
                            db.create_all()
                            logger.info(f"Successfully switched to SQLite fallback: {fallback_db_url}")
                            db_connected = True
                    except:
                        logger.warning("Could not create tables automatically, trying to reconnect")
                        # This is a more aggressive approach to reset the SQLAlchemy connection
                        db.engine.dispose()
                        db.get_engine(app, bind=None)
                        with app.app_context():
                            db.create_all()
                            logger.info("Successfully recreated engine and created tables")
                            db_connected = True
                else:
                    logger.warning("Models not imported, database functionality will be limited")
            except Exception as sqlite_error:
                logger.error(f"SQLite fallback also failed: {sqlite_error}")
                logger.error("Web application will run with severely limited functionality")
        else:
            logger.error("Web application will run with limited functionality")

# Routes
@app.route('/')
def index():
    """Return the main index page"""
    if db_connected:
        return render_template('index.html')
    else:
        # Create a simple template if the database is not connected
        current_db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        is_sqlite = "sqlite" in current_db_url.lower()
        
        error_page = f"""
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Connection Error</title>
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
        .error-container {{
            padding: 50px 20px;
            max-width: 800px;
            margin: 0 auto;
        }}
        .alert-box {{
            padding: 20px;
            border-radius: 5px;
            background-color: rgba(220, 53, 69, 0.2);
            border: 1px solid #dc3545;
            margin-bottom: 20px;
        }}
        .solution-box {{
            padding: 20px;
            border-radius: 5px;
            background-color: rgba(25, 135, 84, 0.2);
            border: 1px solid #198754;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <div class="container error-container">
        <h1>Database Connection Error</h1>
        
        <div class="alert-box">
            <h3>What happened?</h3>
            <p>We couldn't connect to the PostgreSQL database at:</p>
            <pre>{database_url.replace("://", "://<username>:<password>@") if "://" in database_url else database_url}</pre>
            <p>Error: <code>{str(app.config.get("DB_ERROR", "Unknown database error"))}</code></p>
        </div>
        
        <div class="solution-box">
            <h3>Possible Solutions</h3>
            <ol>
                <li>Check if your Neon database project is active</li>
                <li>Verify that your connection credentials are correct</li>
                <li>Update the DATABASE_URL environment variable with valid credentials</li>
                <li>Switch to using SQLite by changing DATABASE_URL to: <code>sqlite:///app.db</code></li>
            </ol>
        </div>
        
        <div class="card">
            <div class="card-body">
                <h3>Current Status</h3>
                <p>Web interface: <span class="badge bg-success">Running</span></p>
                <p>Database connection: <span class="badge bg-danger">Failed</span></p>
                <p>Using SQLite fallback: <span class="badge bg-{"success" if is_sqlite else "danger"}">{"Yes" if is_sqlite else "No"}</span></p>
            </div>
        </div>
        
        <footer class="pt-3 mt-4 text-body-secondary border-top">
            &copy; 2025 Roblox Group Manager Bot
        </footer>
    </div>
</body>
</html>
"""
        return error_page

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
        
        current_db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        db_type = "PostgreSQL" if "postgresql" in current_db_url.lower() else "SQLite"
        db_status = "connected" if db_connected else "disconnected"
        
        return jsonify({
            "status": "online" if bot_running else "offline",
            "message": f"Bot is {'operational' if bot_running else 'not running'} | Database ({db_type}): {db_status}",
            "server_count": "2+",  # Placeholder
            "using_database": db_type,
            "database_connected": db_connected,
            "database_fallback_used": "sqlite" in current_db_url.lower() and "postgresql" in database_url.lower()
        })
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        return jsonify({
            "status": "offline",
            "message": f"Could not check bot status: {str(e)}",
            "database_connected": db_connected
        })

@app.route('/start-bot')
def start_bot():
    """Start the Discord bot as a separate process"""
    try:
        logger.info("Starting Discord bot...")
        import subprocess
        # Use the new workflow script
        process = subprocess.Popen(["python", "discord_bot_workflow.py"])
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
