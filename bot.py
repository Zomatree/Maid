import asyncio
import discord
from utils import database, embed
from discord.ext import commands, flags
import typing
import datetime
import re
import random
import config


class Bot(commands.Bot):
    session = database.DatabaseHandler(**config.database_config)
    cache = {}
    regex = r"\{\{([^{}]+)\}\}"
    group_regex = r"\$([1-9][0-9]*)"
    allowed_attrs = {
        r"{{content}}": lambda ctx, match: ctx.message.content,
        r"{{author_mention}}": lambda ctx, match: ctx.author.mention,
        r"{{author_name}}": lambda ctx, match: ctx.author.name,
        r"{{author_descriminator}}": lambda ctx, match: ctx.author.descriminator,
        r"{{owner_mention}}": lambda ctx, match: f"<@{ctx.guild.owner_id}>",
        r"{{owner_name}}": lambda ctx, match: ctx.guild.get_member(ctx.guild.owner_id).name,
        r"{{owner_descriminator}}": lambda ctx, match: ctx.guild.get_member(ctx.guild.owner_id).descriminator,
    }
    special = {
        r"(rnd|random)\((([^,],)*[^,]+),?\)": lambda ctx, match: random.choice(match.groups(2).split(",")),
    }

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

    async def format_message(self, ctx, args, format):
        format = list(format)
        for match in re.finditer(self.regex, "".join(format)):
            start = match.start(0)
            end = match.end(0)
            group = match.group(1)
            arg = re.match(self.group_regex, group)
            if (arg):
                try:
                    format[start:end] = args[int(arg.group(1))-1]
                except IndexError:
                    pass
            i = 0
            while True:
                converted = False
                for k, v in self.special.items():
                    match = re.match(k, "".join(format)[start+2:end-2])
                    if (match):
                        format[start+2:end-2] = v(ctx, match)
                        converted = True
                if not converted and i:
                    break
                i += 1
            for match in re.finditer(self.regex, "".join(format)):
                print("".join(format)[match.start():match.end()])
                for k, v in self.allowed_attrs.items():
                    allowed_match = re.match(k, match.group(0))
                    if (allowed_match):
                        format[match.start():match.end()] = v(ctx, allowed_match)
            return "".join(format)


bot = Bot("!")
bot.load_extension("jishaku")


@bot.event
async def on_ready():
    rows = await bot.session.get("commands", [], {})
    for row in rows:
        if row[1] not in bot.cache:
            bot.cache[row[1]] = {}
        print(row)
        bot.cache[row[1]][row[0]] = [row[2], row[3]]
        @bot.command(name=row[1])
        @commands.check(lambda _ctx:  _ctx.guild.id in bot.cache[_ctx.command.name])
        async def _command(_ctx, *args):
            await _ctx.send(await bot.format_message(_ctx, args, bot.cache[_ctx.command.name][_ctx.guild.id][0]))
    print("Ready!")


@flags.add_flag("--return", nargs="*")
@flags.add_flag("--args", type=int, default=0)
@bot.flagcommand()
async def create(ctx, name, **options):
    options["return"] = " ".join(options["return"])
    rows = await bot.session.get("commands", [], {"guildid": ctx.guild.id, "name": name})
    if rows:
        return await ctx.send(Embed(bot, ctx, description="A command already exists with that name"))

    await bot.add_custom_command(ctx.guild.id, name, options["return"], options["args"])

    @bot.command(name=name)
    @commands.check(lambda _ctx:  _ctx.guild.id in bot.cache[_ctx.command.name])
    async def _command(_ctx, *args):
        await _ctx.send(await bot.format_message(_ctx, args, bot.cache[_ctx.command.name][_ctx.guild.id][0]))


bot.run(config.TOKEN)
