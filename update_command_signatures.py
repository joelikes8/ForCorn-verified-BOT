#!/usr/bin/env python3
"""
Script to update command signatures in final_discord_bot.py 
from using interaction parameters to using ctx parameters for hybrid commands
"""

import re

def update_command_signatures():
    # Read the file
    with open('final_discord_bot.py', 'r') as file:
        content = file.read()
    
    # Pattern to match function definitions with interaction parameter
    pattern = r'async def ([a-zA-Z_]+)\(interaction: discord\.Interaction(.*?)\):'
    
    # Replace with ctx parameter
    updated_content = re.sub(pattern, r'async def \1(ctx\2):', content)
    
    # Update response handling
    updated_content = updated_content.replace('interaction.response.send_message', 'ctx.send')
    updated_content = updated_content.replace('interaction.response.defer', 'ctx.defer')
    updated_content = updated_content.replace('interaction.followup.send', 'ctx.send')
    updated_content = updated_content.replace('interaction.user', 'ctx.author')
    updated_content = updated_content.replace('interaction.guild', 'ctx.guild')
    updated_content = updated_content.replace('interaction.channel', 'ctx.channel')
    
    # Write the updated content back to the file
    with open('final_discord_bot.py', 'w') as file:
        file.write(updated_content)
    
    print("Updated all command signatures to use ctx instead of interaction")

if __name__ == "__main__":
    update_command_signatures()