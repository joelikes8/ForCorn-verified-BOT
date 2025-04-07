#!/usr/bin/env python
"""
Database Setup Script for ForCorn Discord Bot

This script creates all the necessary database tables based on the models
defined in models.py. It handles both SQLite and PostgreSQL configurations.

Usage:
    python create_db.py
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import app with database configuration
from app import app, db

def setup_database():
    """Set up the database by creating all tables defined in models."""
    print("Starting database setup...")
    
    # Get database URL from environment or default to SQLite
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("WARNING: DATABASE_URL environment variable not set. Using SQLite instead.")
        database_url = "sqlite:///bot.db"
    
    print(f"Using database: {database_url.split('@')[1] if '@' in database_url else database_url}")
    
    try:
        # Import all models to ensure they're registered with SQLAlchemy
        import models
        
        # Create all tables within the Flask application context
        with app.app_context():
            db.create_all()
            print("Tables created successfully:")
            
            # List all created tables
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            for table_name in inspector.get_table_names():
                print(f"  - {table_name}")
                columns = inspector.get_columns(table_name)
                for column in columns:
                    print(f"      {column['name']}: {column['type']}")
        
        print("\nDatabase setup complete!")
        print("\nYou can now run the bot with 'python main.py' or the web app with 'python app.py'")
        
    except Exception as e:
        print(f"Error setting up database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    setup_database()