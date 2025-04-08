"""
This file redirects to the webapp module and provides enhanced error handling.
If the main webapp fails due to database issues, it will use a simpler version.
When run in Discord bot workflow mode, it starts the standalone Discord bot.
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("main")

# Check if we're in Discord bot workflow mode first
if os.environ.get("DISCORD_BOT_WORKFLOW") or os.environ.get("BOT_ONLY_MODE"):
    logger.info("Detected DISCORD_BOT_WORKFLOW or BOT_ONLY_MODE - running standalone Discord bot")
    
    # Set environment variable to ensure it's picked up by child processes
    os.environ["DISCORD_BOT_WORKFLOW"] = "true"
    os.environ["NO_WEB_SERVER"] = "true"
    
    try:
        # Import and run the standalone bot directly
        logger.info("Starting standalone Discord bot...")
        from standalone_discord_bot import main as run_bot
        run_bot()
        sys.exit(0)  # Exit after bot is done
    except ImportError:
        # If we can't directly import, try running it as a separate process
        logger.warning("Could not import standalone_discord_bot directly, trying subprocess")
        try:
            subprocess.run(["python", "standalone_discord_bot.py"], check=True)
            sys.exit(0)  # Exit after process is done
        except Exception as bot_error:
            logger.critical(f"Failed to start standalone bot: {bot_error}")
            sys.exit(1)  # Exit with error code

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
