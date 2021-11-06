import random

from discord import Embed, Color

from modules.commands.base import BaseCommand


class Ball(BaseCommand):
    def __init__(self, channel, author, message, option):
        self.option = option
        self.author = author
        self.message = message
        self.channel = channel
        self.question = message

    async def apply(self):
        embed = Embed(title="Hello World!", description="I'm alive. Hello human.", color="green")
        embed.set_footer(text="Hammer")
        await self.channel.send(embed=embed)
