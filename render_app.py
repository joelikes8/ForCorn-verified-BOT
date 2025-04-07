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
if not os.path.exists('templates/index.html'):
    with open('templates/index.html', 'w') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <title>ForCorn Discord Bot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    <style>
        body {
            padding: 2rem;
        }
        .status-container {
            margin-top: 2rem;
        }
        .card {
            margin-bottom: 1.5rem;
        }
    </style>
</head>
<body data-bs-theme="dark">
    <div class="container">
        <div class="row">
            <div class="col-12">
                <h1 class="display-4 mb-4">ForCorn Discord Bot</h1>
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Bot Status</h5>
                        <p class="card-text">
                            <span id="status-badge" class="badge bg-secondary">Checking...</span>
                            <span id="status-message">Checking bot status...</span>
                        </p>
                        <p class="card-text" id="server-count"></p>
                    </div>
                </div>
                
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Bot Features</h5>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Roblox Verification</li>
                            <li class="list-group-item">Group Rank Management</li>
                            <li class="list-group-item">Support Tickets</li>
                            <li class="list-group-item">Server Moderation</li>
                            <li class="list-group-item">Anti-Raid Protection</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Function to check bot status
        function checkStatus() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    const statusBadge = document.getElementById('status-badge');
                    const statusMessage = document.getElementById('status-message');
                    const serverCount = document.getElementById('server-count');
                    
                    if (data.status === 'online') {
                        statusBadge.className = 'badge bg-success';
                        statusBadge.textContent = 'Online';
                        statusMessage.textContent = data.message;
                        
                        if (data.server_count) {
                            serverCount.textContent = `Serving ${data.server_count} Discord servers`;
                        }
                    } else if (data.status === 'initializing') {
                        statusBadge.className = 'badge bg-warning';
                        statusBadge.textContent = 'Starting';
                        statusMessage.textContent = data.message;
                    } else {
                        statusBadge.className = 'badge bg-danger';
                        statusBadge.textContent = 'Error';
                        statusMessage.textContent = data.message;
                    }
                })
                .catch(error => {
                    const statusBadge = document.getElementById('status-badge');
                    const statusMessage = document.getElementById('status-message');
                    
                    statusBadge.className = 'badge bg-danger';
                    statusBadge.textContent = 'Error';
                    statusMessage.textContent = 'Failed to connect to the server';
                });
        }
        
        // Check status on page load
        checkStatus();
        
        // Check status every 30 seconds
        setInterval(checkStatus, 30000);
    </script>
</body>
</html>""")

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

# Start the bot in a separate thread
if os.environ.get("START_BOT", "true").lower() == "true":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    print("Bot thread started")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)