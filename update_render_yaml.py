"""
Script to update render.yaml to fix port binding issues
"""

updated_render_yaml = """services:
  # Discord Bot Service
  - type: worker
    name: forcorn-discord-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python start_simple.py
    envVars:
      - key: DISCORD_TOKEN
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: forcorn-bot-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: PYTHONPATH
        value: "."
      - key: PYTHON_UNBUFFERED
        value: "1"

  # Web Interface Service
  - type: web
    name: forcorn-web
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn flask_app:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120 --access-logfile - --error-logfile -
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: forcorn-bot-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: SESSION_SECRET
        generateValue: true
      - key: START_BOT
        value: "false"
      - key: PYTHONPATH
        value: "."
      - key: PYTHON_UNBUFFERED
        value: "1"

databases:
  - name: forcorn-bot-db
    databaseName: forcornbot
    user: forcorn
    plan: free
"""

# Write the updated YAML to the file
with open("render.yaml", "w") as f:
    f.write(updated_render_yaml)

print("render.yaml has been updated successfully!")