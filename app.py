import os
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    print("WARNING: DATABASE_URL environment variable not set. Using SQLite instead.")
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
    # Import models here to avoid circular imports
    import models
    db.create_all()

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

# Create necessary templates directory and basic template
os.makedirs('templates', exist_ok=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)