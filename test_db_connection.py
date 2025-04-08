import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the connection string
db_url = os.environ.get("DATABASE_URL", "postgresql://neondb_owner:npg_GwOlJ4tfy7ak@ep-shy-glitter-a4f7cjs2.us-east-1.aws.neon.tech/neondb?sslmode=require")

print(f"Attempting to connect to database...")
print(f"Connection string: {db_url.replace('://', '://********:********@')}")

try:
    # Try to connect
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Execute a simple query
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    print(f"Connection successful! Query result: {result}")
    
    # Close the connection
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"ERROR: Could not connect to the database!")
    print(f"Error details: {str(e)}")
    
    # Recommend alternatives
    print("\nPossible solutions:")
    print("1. Check if your Neon project is active at https://console.neon.tech/")
    print("2. Verify that your connection credentials are correct")
    print("3. Try creating a new database endpoint or generate new credentials")
    print("4. Use SQLite as a fallback: DATABASE_URL=sqlite:///app.db")
    
    sys.exit(1)