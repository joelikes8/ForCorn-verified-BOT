#!/usr/bin/env python3
"""
Script to update command decorators in the final_discord_bot.py file
from @bot.slash_command to @bot.hybrid_command
"""

import re

def update_commands():
    # Read the file
    with open('final_discord_bot.py', 'r') as file:
        content = file.read()
    
    # Replace slash_command with hybrid_command
    updated_content = re.sub(r'@bot\.slash_command', '@bot.hybrid_command', content)
    
    # Write the updated content back to the file
    with open('final_discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Updated all commands from slash_command to hybrid_command")

if __name__ == "__main__":
    update_commands()