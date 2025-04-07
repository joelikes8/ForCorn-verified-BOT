#!/usr/bin/env python3

content = """services:
  - type: web
    name: forcorn-bot
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn webapp:app --bind 0.0.0.0:$PORT --log-level debug --timeout 120 --access-logfile - --error-logfile -
    envVars:
      - key: PORT
        value: 10000
      - key: DISCORD_TOKEN
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: forcorn-bot-db
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.10.0
      - key: SESSION_SECRET
        generateValue: true
      - key: START_BOT
        value: "true"

databases:
  - name: forcorn-bot-db
    databaseName: forcornbot
    user: forcorn
    plan: free
"""

with open('render.yaml', 'w') as f:
    f.write(content)

print("render.yaml updated successfully!")