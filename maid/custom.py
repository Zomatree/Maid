from discord.ext import commands, flags
import discord
from . import utils

def setup(bot):

    @flags.add_flag("--return", nargs="*")
    @flags.add_flag("--args", type=int, default=0)
    @bot.flagcommand()
    async def create(ctx, name, **options):
        options["return"] = " ".join(options["return"])
        rows = await bot.session.get("commands", [], {"guildid": ctx.guild.id, "name": name})
        if rows:
            return await ctx.send(utils.Embed(bot, ctx, description="A command already exists with that name"))

        await bot.add_custom_command(ctx.guild.id, name, options["return"], options["args"])

        bot.create_custom_command(name)