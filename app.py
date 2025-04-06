import os
import json
from flask import Flask, render_template, jsonify, request, redirect, url_for
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default-secret-key")

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Status route to check if the bot is online
@app.route('/api/status')
def status():
    try:
        # Check if data directory exists as a simple check
        if os.path.exists('data'):
            # Count number of configs if any
            config_count = 0
            if os.path.exists('data/server_configs.json'):
                with open('data/server_configs.json', 'r') as f:
                    config_data = json.load(f)
                    config_count = len(config_data)
            
            return jsonify({
                'status': 'online',
                'message': 'Bot is running',
                'server_count': config_count
            })
        else:
            return jsonify({
                'status': 'initializing',
                'message': 'Bot is starting up'
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