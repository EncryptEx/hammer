import discord
from discord.ext import commands
import datetime

from get_enviroment import TOKEN, COMMAND_PREFIX
from modules.commands.helloWorld import HelloWorld
# from modules.commands.welcomeUser import WelcomeUser


class Hammer:

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.messages = True
        print(intents)
        self.client = commands.Bot(COMMAND_PREFIX, guild_subscriptions=True, self_bot=False, intents=intents)
        self.token = TOKEN
        self.client.remove_command('help')

        @self.client.event
        async def on_ready():
            await self.client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="you",))
            print("I'm ready. ",datetime.datetime.now())

        # @self.client.event
        # async def on_member_join(member):
        #     await WelcomeUser(member=member, client=self.client).apply()

        @self.client.event
        async def on_message(message):
            # print("message recieved:",message)
            message_text = message.content.lower().split(' ')
            if message_text[0].startswith(COMMAND_PREFIX):
                command = message_text[0][1:]
                channel = message.channel
                author = message.author
                print(command, channel, author, str(command) == 'hello')

                if str(command) == 'hello':
                    await HelloWorld(channel=channel, author=author, message=message_text).apply()
    def start(self):
        print("Starting modules!")
        self.client.run(self.token)
