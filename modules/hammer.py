import discord
from discord.ext import commands
import time

from get_enviroment import TOKEN, COMMAND_PREFIX
from modules.commands.helloWorld import HelloWorld
# from modules.commands.welcomeUser import WelcomeUser


class Hammer:

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.message = True
        self.client = commands.Bot(COMMAND_PREFIX, guild_subscriptions=True, self_bot=False, intents=intents)
        self.token = TOKEN
        self.client.remove_command('help')

        @self.client.event
        async def on_ready():
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you",))
            await print("I'm ready. ",time.gmtime(time.time))

        # @self.client.event
        # async def on_member_join(member):
        #     await WelcomeUser(member=member, client=self.client).apply()

        @self.client.event
        async def on_message(message):
            message_text = message.content.lower().split(' ')
            if len(message_text) > 1 and message_text[0].startswith(COMMAND_PREFIX):
                command = message_text[1]
                channel = message.channel
                author = message.author
                if command == 'hello':
                    HelloWorld(channel=channel, author=author)
    def start(self):
        print("Starting modules!")
        self.client.run(self.token)
