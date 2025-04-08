"""
This file redirects to the webapp module and provides enhanced error handling
"""
import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

try:
    from webapp import app
    logger.info("Successfully imported app from webapp module")
except Exception as e:
    logger.error(f"Error importing app: {str(e)}")
    from flask import Flask
    app = Flask(__name__)
    
    @app.route('/')
    def error_page():
        return """
        <html>
            <head><title>Database Error</title></head>
            <body>
                <h1>Database Connection Error</h1>
                <p>There was an error connecting to the database. Please check your configuration.</p>
                <p>Error details: {}</p>
            </body>
        </html>
        """.format(str(e))
    
    logger.info("Created fallback app due to import error")

# For direct execution
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
