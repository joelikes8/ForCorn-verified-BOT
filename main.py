"""
This file redirects to the webapp module
"""
from webapp import app

# The app object is imported from webapp.py
# This allows gunicorn to find the app object when started with main:app
