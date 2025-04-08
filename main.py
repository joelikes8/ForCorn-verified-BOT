"""
This file redirects to the webapp module and provides enhanced error handling.
If the main webapp fails due to database issues, it will use a simpler version.
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

# First, try to import from the normal webapp
try:
    from webapp import app
    logger.info("Successfully imported app from webapp module")
except Exception as e:
    # If that fails, try the simple version that doesn't need a database
    logger.error(f"Error importing webapp: {str(e)}")
    logger.info("Trying simple_webapp instead...")
    
    try:
        from simple_webapp import app
        logger.info("Successfully imported app from simple_webapp module")
    except Exception as e2:
        # If both fail, create a very basic Flask app
        logger.error(f"Error importing simple_webapp: {str(e2)}")
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def error_page():
            return f"""
            <html>
                <head><title>Critical Error</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    pre {{ background: #f4f4f4; padding: 15px; overflow: auto; }}
                </style>
                </head>
                <body>
                    <h1>Critical Application Error</h1>
                    <p>There was a critical error starting the application.</p>
                    <h3>Primary Error:</h3>
                    <pre>{str(e)}</pre>
                    <h3>Secondary Error:</h3>
                    <pre>{str(e2)}</pre>
                    <p>Please check your configuration and dependencies.</p>
                </body>
            </html>
            """
        
        logger.info("Created emergency fallback app due to import errors")

# For direct execution
if __name__ == "__main__":
    # Only start the web server if not in discord bot workflow mode
    if not os.environ.get("DISCORD_BOT_WORKFLOW") and not os.environ.get("NO_WEB_SERVER"):
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=True)
    else:
        logger.info("Web server disabled due to DISCORD_BOT_WORKFLOW or NO_WEB_SERVER being set")
