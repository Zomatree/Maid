from discord.ext import commands, flags
import discord
from maid import utils
from maid import config


def setup(bot):

    @flags.add_flag("--return", "-R", nargs="*")
    @flags.add_flag("--description", '-D', nargs="*", default="a custom command")
    @flags.add_flag("--args", "-A", type=int, default=0)
    @bot.flagcommand()
    async def create(ctx, name, **options):
        """\tthis is the command for making custom commands in @Maid,
    all formatting messages are incased in {{...}}, if any variables are not inside {{...}} they will not be formatted.
    possible formatting that there are:

    Argument formattings:
        this allows you to `{{$1}}` for example and this will turn into the first argument in the command when the the command is run,
        the command arguemnts start at 1 not 0.

    Regular formattings:
        {}

    Special formattings:
        {}
        """
        options["return"] = " ".join(options["return"])
        options["description"] = " ".join(options["description"])
        rows = await bot.session.get("commands", [], {"guildid": ctx.guild.id, "name": name})
        if rows:
            return await ctx.send(utils.Embed(bot, ctx, description="A command already exists with that name"))

        await bot.add_custom_command(ctx.guild.id, name, options["return"], options["args"], options["description"])

        bot.create_custom_command(name, options["description"])
    callback = create.callback
    create.update(help = callback.__doc__.format("\n\t\t".join(config.allowed_attrs_names), "\n\t\t".join(config.special_names)))