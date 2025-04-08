"""
Simple web application for ForCorn Discord Bot

This is a minimalist version of the web interface that works even when
database connections fail. It provides basic status information and
a way to start the bot without requiring database access.
"""

import os
import sys
import logging
import subprocess
from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("simple_webapp")

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key-for-development")

# Get database URL (for display only, we don't use it)
database_url = os.environ.get("DATABASE_URL", "No database URL configured")

# The simple HTML template
ERROR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Database Connection Error</title>
    <link rel="stylesheet" href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css">
    <style>
        .error-container {
            padding: 50px 20px;
            max-width: 800px;
            margin: 0 auto;
        }
        .alert-box {
            padding: 20px;
            border-radius: 5px;
            background-color: rgba(220, 53, 69, 0.2);
            border: 1px solid #dc3545;
            margin-bottom: 20px;
        }
        .solution-box {
            padding: 20px;
            border-radius: 5px;
            background-color: rgba(25, 135, 84, 0.2);
            border: 1px solid #198754;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container error-container">
        <h1>Database Connection Error</h1>
        
        <div class="alert-box">
            <h3>What happened?</h3>
            <p>We couldn't connect to the PostgreSQL database at:</p>
            <pre>{db_url_masked}</pre>
            <p>Error: <code>{error_message}</code></p>
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
        
        <div class="card mb-4">
            <div class="card-body">
                <h3>Current Status</h3>
                <p>Web interface: <span class="badge bg-success">Running</span></p>
                <p>Database connection: <span class="badge bg-danger">Failed</span></p>
                <p>Using emergency mode: <span class="badge bg-warning">Yes</span></p>
            </div>
        </div>
        
        <div class="card mb-4">
            <div class="card-body">
                <h3>Start Discord Bot</h3>
                <p>You can still start the Discord bot in fallback mode:</p>
                <button id="startBotBtn" class="btn btn-primary">Start Discord Bot</button>
                <div id="botStatus" class="mt-3"></div>
            </div>
        </div>
        
        <footer class="pt-3 mt-4 text-body-secondary border-top">
            &copy; 2025 Roblox Group Manager Bot
        </footer>
    </div>
    
    <script>
        document.getElementById('startBotBtn').addEventListener('click', function() {
            const statusDiv = document.getElementById('botStatus');
            statusDiv.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div> Starting bot...';
            
            fetch('/start-bot')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') {
                        statusDiv.innerHTML = '<div class="alert alert-success">Bot started successfully!</div>';
                    } else {
                        statusDiv.innerHTML = '<div class="alert alert-danger">Error: ' + data.message + '</div>';
                    }
                })
                .catch(error => {
                    statusDiv.innerHTML = '<div class="alert alert-danger">Error: Could not start bot</div>';
                });
        });
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def index():
    """Return the main index page"""
    # We always show the error page in simple mode
    masked_url = database_url.replace("://", "://<username>:<password>@") if "://" in database_url else database_url
    return render_template_string(ERROR_TEMPLATE, 
                              db_url_masked=masked_url,
                              error_message="Using emergency mode due to database connection failure")

@app.route('/status')
def status():
    """Return the status of the application"""
    return jsonify({
        "status": "limited",
        "message": "ForCorn Bot web interface is running in emergency mode",
        "version": "1.0.0",
        "database_available": False,
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
            "status": "limited" if bot_running else "offline",
            "message": f"Bot is {'operational' if bot_running else 'not running'} | Database: disconnected",
            "server_count": "N/A",
            "using_database": "None",
            "database_connected": False,
            "emergency_mode": True
        })
    except Exception as e:
        logger.error(f"Error checking bot status: {e}")
        return jsonify({
            "status": "offline",
            "message": f"Could not check bot status: {str(e)}",
            "database_connected": False
        })

@app.route('/start-bot')
def start_bot():
    """Start the Discord bot as a separate process"""
    try:
        logger.info("Starting Discord bot in emergency mode...")
        process = subprocess.Popen(["python", "discord_bot_workflow.py"])
        logger.info(f"Started Discord bot (PID: {process.pid})")
        return jsonify({
            "status": "ok",
            "message": "Discord bot started in emergency mode",
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