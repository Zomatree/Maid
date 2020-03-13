import discord
import typing
from discord.ext import commands
import asyncio
import datetime
import random


class Embed(discord.Embed):
    def __init__(self, bot, message: typing.Union[commands.Context, discord.Message] = None, **kwargs):
        super().__init__(**kwargs)
        asyncio.create_task(self.__ainit__(bot, message, **kwargs))

    async def __ainit__(self, bot, message, **kwargs):
        self._colour = discord.Colour.from_hsv(random.random(), 1, 1)
        if isinstance(message, commands.Context):
            message = message.message
        title = kwargs.get("title")
        if title:
            kwargs.pop("title")

        if title:
            avatar_url = message.author.avatar_url_as(format="png") if message else None
            self.set_author(name=title, icon_url=avatar_url)

        icon_url = bot.user.avatar_url_as(format="png")
        self.set_footer(icon_url=icon_url)

        self._timestamp = datetime.datetime.utcnow()