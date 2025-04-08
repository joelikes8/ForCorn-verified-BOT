"""
Explicit port binding test for Render.com deployment.
This file establishes a simple Flask app that binds to the PORT environment variable.
"""

import os
import logging
from flask import Flask, jsonify

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Simple root endpoint to verify the app is running"""
    logger.info("Root endpoint accessed")
    return jsonify({
        "status": "ok",
        "message": "Port binding test successful",
        "port": os.environ.get("PORT", "5000"),
        "environment": os.environ.get("RENDER", "local")
    })

# Run the app with explicit port binding
if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    logger.info(f"Starting app on port {port}")
    # Bind to all interfaces (0.0.0.0) so the app is externally accessible
    app.run(host="0.0.0.0", port=port)