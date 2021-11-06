import random

from discord import Embed

from modules.commands.base import BaseCommand


class HelloWorld(BaseCommand):
    def __init__(self, channel, author, message):
        self.author = author
        self.message = message
        self.channel = channel

    async def apply(self):
        embed = Embed(title="Hello World!", description="I'm alive. Hello human.")
        embed.set_footer(text="Hammer")
        await self.channel.send(embed=embed)
