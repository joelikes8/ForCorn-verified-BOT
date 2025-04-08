"""
Script to update render.yaml to use discord_main.py
"""

import re

# Read the current render.yaml file
with open("render.yaml", "r") as f:
    content = f.read()

# Replace start_simple.py with discord_main.py
content = content.replace(
    "startCommand: python start_simple.py",
    "startCommand: python discord_main.py"
)

# Write the updated content back to render.yaml
with open("render.yaml", "w") as f:
    f.write(content)

print("render.yaml has been updated to use discord_main.py")