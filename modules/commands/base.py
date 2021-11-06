from abc import ABC, abstractmethod

from discord.utils import get


class BaseCommand(ABC):
    def __init__(self, channel, author):
        self.channel = channel
        private = getattr(channel, "guild", None) is not None
        if private:
            self.author = get(channel.guild.members, id=author.id)
        else:
            self.author = author
        self.user = author

    @abstractmethod
    async def apply(self):
        pass
