import asyncio
import discord
from . import utils, config
from discord.ext import commands, flags
import typing
import datetime
import re
import random
import logging
from inspect import isawaitable

logging.basicConfig(level=logging.INFO)


class Bot(commands.Bot):
    session = utils.database.DatabaseHandler(**config.database_config)
    cache = {}
    regex = r"\{\{([^{}]+)\}\}"
    group_regex = r"{{\$([1-9][0-9]*)}}"
    allowed_attrs = {
        r"{{content}}": lambda ctx, match: ctx.message.content[len(ctx.prefix)+len(ctx.command.name):],
        r"{{author_mention}}": lambda ctx, match: ctx.author.mention,
        r"{{author_name}}": lambda ctx, match: ctx.author.name,
        r"{{author_discriminator}}": lambda ctx, match: ctx.author.discriminator,
        r"{{owner_mention}}": lambda ctx, match: f"<@{ctx.guild.owner_id}>",
        r"{{owner_name}}": lambda ctx, match: ctx.guild.get_member(ctx.guild.owner_id).name,
        r"{{owner_discriminator}}": lambda ctx, match: ctx.guild.get_member(ctx.guild.owner_id).discriminator,
    }
    special = {
        r"{{(rnd|random)\((([^,],)*[^,]+),?\)}}": lambda ctx, match: random.choice(match.group(2).split(",")),
    }

    async def on_ready(self):
        self.load_extension("jishaku")
        rows = await self.session.get("commands", [], {})
        for row in rows:
            if row[1] not in self.cache:
                self.cache[row[1]] = {}
            self.cache[row[1]][row[0]] = [row[2], row[3]]
            self.create_custom_command(row[1])
        print("Ready!")

    def create_custom_command(self, name):

        @self.command(name=name)
        @commands.check(lambda _ctx:  _ctx.guild.id in _ctx.bot.cache[_ctx.command.name])
        async def _command(_ctx, *args):
            await _ctx.send(await self.format_message(_ctx, "".join(args), self.cache[_ctx.command.name][_ctx.guild.id][0]))

    async def add_custom_command(self, guildid, name, returnstr, args):
        await self.session.insert("commands", [guildid, name, returnstr, args])
        if name not in self.cache:
            self.cache[name] = {}
        self.cache[name][guildid] = [returnstr, args]

    def flagcommand(self, *args, **kwargs):
        def inner(command):
            flag = flags.command(*args, **kwargs)(command)
            self.add_command(flag)
            return flag
        return inner

    async def call_func(self, f, *args):
        ret = f(*args)
        if isawaitable(ret):
            ret = await ret
        return str(ret)

    async def format_message(self, ctx, args, strformat):
        strformat = list(strformat)

        while True:
            found = False
            match = re.search(self.regex, "".join(strformat))  # hello -> {{$1}} <-
            if not match or not "".join(strformat)[match.start(1):match.end(1)]:
                break

            content = "".join(strformat)[match.start():match.end()]
            arg = re.match(self.group_regex, content)  # checking for {{$1}}
            if arg:
                try:
                    strformat[match.start():match.end()] = args[int(arg.group(1))-1]  # {{$1}} -> args[1-1] command arg indexes will start at 1 so need to minus 1
                except IndexError:
                    pass  # if the number is more than the total amount of args, TODO: check this when creating the command
                found = True

            for regex, func in self.special.items():
                special_match = re.match(regex, content)
                if special_match:
                    strformat[match.start(1):match.end(1)] = await self.call_func(func, ctx, special_match)  # replaces the stuff inside the {{}} so the return of the funcs can be dynamic.
                    found = True

            for regex, func in self.allowed_attrs.items():
                attr_match = re.match(regex, content)  # checking for {{author_name}} or similar
                if attr_match:
                    strformat[match.start():match.end()] = await self.call_func(func, ctx, attr_match)
                    found = True

            if not found:
                strformat[match.start():match.end()] = strformat[match.start(1):match.end(1)]

        return "".join(strformat)