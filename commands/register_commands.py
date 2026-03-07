import requests
import yaml
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN")
APPLICATION_ID = os.getenv("APPLICATION_ID")

if not TOKEN:
    raise RunTimeError("Missing bot token.  Either set it in your environment variables or add it to the .env file")
if not APPLICATION_ID:
    raise RunTimeError("Missing application ID.  Either set it in your environment variables or add it to the .env file")


URL = f"https://discord.com/api/v9/applications/{APPLICATION_ID}/commands"


with open("discord_commands.yaml", "r") as file:
    yaml_content = file.read()

commands = yaml.safe_load(yaml_content)
headers = {"Authorization": f"Bot {TOKEN}", "Content-Type": "application/json"}

# Send the POST request for each command
for command in commands:
    response = requests.post(URL, json=command, headers=headers)
    command_name = command["name"]
    print(f"Command {command_name} created: {response.status_code}")
