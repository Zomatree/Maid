import asyncio
import discord
from maid import utils, config
from discord.ext import commands, flags
import re
import random
from inspect import isawaitable

class CustomCommands(commands.Cog, name="custom commands"):
    pass

custom_commands = CustomCommands()

class Bot(commands.Bot):
    session = utils.database.DatabaseHandler(**config.database_config)
    cache = {}
    ran = False

    async def on_ready(self):
        if not self.ran:
            self.load_extension("jishaku")
            self.add_cog(custom_commands)
            rows = await self.session.get("commands", [], {})
            for row in rows:
                if row[1] not in self.cache:
                    self.cache[row[1]] = {}
                self.cache[row[1]][row[0]] = [row[2], row[3], row[4], row[5]]
                self.create_custom_command(row[1], row[4], row[5])
            print("Ready!")
        self.ran = True

    def create_custom_command(self, name, desc, aliases):
        if not self.get_command(name):
            @self.command(name=name, help=desc)
            @commands.check(lambda _ctx: _ctx.invoked_with in [_ctx.command.name] + self.cache[_ctx.command.name][_ctx.guild.id][3])
            @commands.check(lambda _ctx:  _ctx.guild.id in _ctx.bot.cache[_ctx.command.name])
            async def _command(_self, _ctx):
                await _ctx.send(await self.format_message(_ctx, "", self.cache[_ctx.command.name][_ctx.guild.id][0]))
            _command.cog = custom_commands  # TODO: find out why they dont actually appear inside the cog
            custom_commands.__cog_commands__ += (_command,)

        for alias in aliases:
            if alias not in self.all_commands:
                self.all_commands[alias] = self.all_commands[name]

    async def add_custom_command(self, guildid, name, returnstr, args, desc, aliases):
        await self.session.insert("commands", [guildid, name, returnstr, args, desc, aliases])
        if name not in self.cache:
            self.cache[name] = {}
        self.cache[name][guildid] = [returnstr, args, desc, aliases]

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
            match = re.search(config.regex, "".join(strformat))  # hello -> {{$1}} <-
            if not match or not "".join(strformat)[match.start(1):match.end(1)]:
                break

            content = "".join(strformat)[match.start():match.end()]
            arg = re.match(config.group_regex, content)  # checking for {{$1}}
            if arg:
                try:
                    strformat[match.start():match.end()] = args[int(arg.group(1))-1]  # {{$1}} -> args[1-1] command arg indexes will start at 1 so need to minus 1
                except IndexError:
                    pass  # if the number is more than the total amount of args, TODO: check this when creating the command
                found = True

            for regex, func in config.special.items():
                special_match = re.match(regex, content)
                if special_match:
                    strformat[match.start(1):match.end(1)] = await self.call_func(func, ctx, special_match)  # replaces the stuff inside the {{}} so the return of the funcs can be dynamic.
                    found = True

            for regex, func in config.allowed_attrs.items():
                attr_match = re.match(regex, content)  # checking for {{author_name}} or similar
                if attr_match:
                    strformat[match.start():match.end()] = await self.call_func(func, ctx, attr_match)
                    found = True

            if not found:
                strformat[match.start():match.end()] = strformat[match.start(1):match.end(1)]

        return "".join(strformat)

    async def on_command(self, ctx):
        print(ctx.command)
        print(self.cache.keys())
        if ctx.command.name in self.cache.keys():
            await self.session.insert("stats", [ctx.command.name, ctx.author.id, ctx.guild.id])
