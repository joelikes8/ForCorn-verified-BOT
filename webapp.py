import os
import json
import threading
import subprocess
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

# Create necessary templates directory and basic template if it doesn't exist
os.makedirs('templates', exist_ok=True)

# Bot process
bot_process = None

def start_bot():
    global bot_process
    try:
        # Start the Discord bot in a separate process
        bot_process = subprocess.Popen(['python', 'main.py'], 
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.STDOUT,
                                      text=True)
        
        # Log bot output
        while True:
            line = bot_process.stdout.readline()
            if not line:
                break
            print(f"BOT: {line.strip()}")
            
    except Exception as e:
        print(f"Error starting bot: {e}")

# Start the bot in a separate thread if environment variable is set
if os.environ.get("START_BOT", "true").lower() == "true":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("Bot thread started")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    # Print the port we're binding to - helpful for debugging
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)