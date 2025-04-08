import os
import sys
import logging
from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

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

# Initialize database
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # Needed for url_for to generate with https

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

# Initialize app with extensions
db.init_app(app)

# Create necessary templates directory and basic template if it doesn't exist
os.makedirs('templates', exist_ok=True)

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

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Status route for health checks
@app.route('/api/status')
def status():
    try:
        return jsonify({
            'status': 'online',
            'message': 'Web API is running'
        })
    except Exception as e:
        logger.error(f"Error in /api/status endpoint: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
