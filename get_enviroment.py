import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
COMMAND_PREFIX = os.getenv("PREFIX")
OWNER = os.getenv("OWNER")
ANNOUNCEMENTS_CHANNEL = os.getenv("ANNOUNCEMENTS")
