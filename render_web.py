"""
Special entry point for Render.com web service deployment.
This file ensures that the application correctly binds to the PORT
provided by Render.com's environment variables.
"""

import os
from flask_app import app

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)