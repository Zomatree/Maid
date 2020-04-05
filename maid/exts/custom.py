from discord.ext import commands, flags, menus
import discord
from maid import utils
from maid import config


class ListPageSource(menus.ListPageSource):
    def __init__(self, data, ctx, **attrs):
        super().__init__(data, per_page=5)
        self.ctx = ctx
        self.attrs = attrs

    async def format_page(self, menu, entries):
        embed = utils.Embed(self.ctx.bot, self.ctx, **self.attrs)
        embed.set_footer(icon_url=str(self.ctx.bot.user.avatar_url_as(format="png")), text=f"page {menu.current_page+1}/{self.get_max_pages() or 1}")
        embed.description = "\n".join([f"{i}. {string}" for i, string in enumerate(entries, 1)])
        return {"embed": embed}

def setup(bot):

    @flags.add_flag("--description", '-D', nargs="*", default=["a custom command"])
    @flags.add_flag("--aliases", "-A", nargs="*", default=[])
    @bot.flagcommand()
    async def create(ctx, name, *, content, **options):
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

    Example:
        `maid create command_name hello {{author_mention}} --description this message here will appear in the "maid help" command`
        """
        options["description"] = " ".join(options.get("description", [])) or "A custom command"
        options["aliases"] = options.get("aliases", [])
        rows = await bot.session.get("commands", [], {"guildid": ctx.guild.id, "name": name})
        if rows:
            return await ctx.send(embed=utils.Embed(bot, ctx, description="A command already exists with that name"))

        await bot.add_custom_command(ctx.guild.id, name, content, 0, options["description"], options.get("aliases", []))

        bot.create_custom_command(name, options["description"], options["aliases"] or [])
        await ctx.send(embed=utils.Embed(bot, ctx, colour=0x00FF00, description=f"Successfully created a command called {name}"))

    callback = create.callback
    create.update(help = callback.__doc__.format("\n\t\t".join(config.allowed_attrs_names), "\n\t\t".join(config.special_names)))

    @bot.command()
    async def delete(ctx, *, name):
        """Deletes a custom command and all the aliases pointed to it
    
    Example:
        `maid delete command_name`
        """
        try:
            aliases = bot.cache[name].pop(ctx.guild.id)[3]
            for i, command in enumerate(bot.cogs["custom commands"].__cog_commands__):
                if command.name in [name, *aliases]:
                    bot.cogs["custom commands"].__cog_commands__.pop(i)
            del bot.all_commands[name]
            for alias in aliases:
                del bot.all_commands[alias]
            await ctx.send(embed=utils.Embed(bot, ctx, colour=0x00FF00, description=f"Successfully deleted {name} and all its aliases"))
        except KeyError:
            await ctx.send(embed=utils.Embed(bot, ctx, colour=0xFF0000, description=f"No command called {name} in this guild, please make sure its not an alias name"))

    @bot.command()
    async def alias(ctx, alias, *,  command):
        """creates an alias to a custom command, this cannot be the name of any existing custom commands or built in commands to the bot

    Example:
            `maid alias my_alias command1`
        """
        if alias == command:
            return await ctx.send(embed=utils.Embed(bot, ctx, colour=0xFF0000, description=f"cannot create a alias called that for that command"))
        if command in [c.name for c in bot.commands if c.name not in bot.cache.keys()]:
            return await ctx.send(embed=utils.Embed(bot, ctx, colour=0xFF0000, description=f"cannot create a alias for that command"))
        if command not in bot.cache.keys():
            return await ctx.send(embed=utils.Embed(bot, ctx, colour=0xFF0000, description=f"No command called {command} in this guild, please make sure its not an alias name"))

        await ctx.send(embed=utils.Embed(bot, ctx, colour=0x00FF00, description=f"Successfully created an alias called {alias} pointing to {command}"))
        bot.all_commands[alias] = bot.all_commands[command]
        bot.cache[command][ctx.guild.id][3].append(alias)

    @bot.command()
    async def stats(ctx):
        """Gets the top used commands in the server
        
    Example:
        `maid stats`"""
        commands = await bot.session.get("stats", ["command"], {"guildid": ctx.guild.id})
        stat = {}
        
        for command in commands:
            command = command[0]
            if command not in stat:
                stat[command] = 0
            stat[command] += 1
        
        pages = menus.MenuPages(ListPageSource([f"{v} - {k}" for k, v in stat.items()], ctx, title=f"Total commands used {len(commands)}"), clear_reactions_after=True, timeout=120)
        await pages.start(ctx)

    @bot.command(aliases=["user", "player"])
    async def member(ctx, member: discord.Member=None):
        """Shows statistics about member for custom commands
        
    Example:
        `maid stats member @member`
        `maid stats member` - this will do it for yourself"""
        member = member or ctx.author
        commands = await bot.session.get("stats", ["command"], {"guildid": ctx.guild.id, "authorid": member.id})
        stat = {}
        
        for command in commands:
            command = command[0]
            if command not in stat:
                stat[command] = 0
            stat[command] += 1
        
        pages = menus.MenuPages(ListPageSource([f"{v} - {k}" for k, v in stat.items()], ctx, title=f"Commands used {len(commands)}"), clear_reactions_after=True, timeout=120)
        await pages.start(ctx)

    @bot.command()
    async def command(ctx, command: utils.CommandConverter):
        """Shows statistics about command for custom commands
        
    Example:
        `maid stats command customcommand1`
        """
        result = await bot.session.get("stats", ["authorid"], {"guildid": ctx.guild.id})
        uses = len(result)
        stat = {}

        for id in result:
            id = id[0]
            if id not in stat:
                stat[id] = 0
            stat[id] += 1

        pages = menus.MenuPages(ListPageSource([f"{v} - <@{k}>" for k, v in sorted(stat.items(), key=lambda k: k[1], reverse=True)], ctx, title=f"Uses: {uses}"), clear_reactions_after=True, timeout=120)
        await pages.start(ctx)
