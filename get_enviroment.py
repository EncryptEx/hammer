import os

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
COMMAND_PREFIX = os.getenv("PREFIX", "/")
OWNER = os.getenv("OWNER")
ANNOUNCEMENTS_CHANNEL = os.getenv("ANNOUNCEMENTS")
DEV_SUGGESTIONS_CHANNEL = os.getenv("DEVSUGGESTIONS")
SECURITY_GUILD = os.getenv("SECURITYGUILD")
SECURITY_CHANNEL = os.getenv("SECURITY")
SWEAR_WORDS_LIST = [i.lower().replace("_", " ") for i in os.getenv("BANNEDWORDS", []).split(",")]
