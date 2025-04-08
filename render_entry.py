"""
Special entry point for Render.com web service deployment.
This file ensures proper port binding for Render.com deployment.
"""

import os
from webapp import app

# This file is specifically designed for Render.com deployment
# It explicitly binds to the PORT environment variable

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.environ.get("PORT", 5000))
    # Note that we bind to 0.0.0.0 to ensure the application is accessible
    app.run(host="0.0.0.0", port=port, debug=False)