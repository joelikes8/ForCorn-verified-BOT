"""
Main web application entry point

This file is responsible for running the Flask web application
without starting the Discord bot. It's meant to be used as an
entry point for Gunicorn or other WSGI servers.
"""

import os
import logging
import sys
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Import the Flask application
from app import app

# Route definitions
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
        "version": "1.0.0"
    })

# Only run the server directly if this file is executed directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)