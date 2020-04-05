import discord
from discord.ext import commands
from discord.ext import menus
from maid import utils


class BotHelpCommand(menus.ListPageSource):
    def __init__(self, data, ctx, name, value, **attrs):
        super().__init__(data, per_page=5)
        self.ctx = ctx
        self.name = name
        self.value = value
        self.attrs = attrs

    async def format_page(self, menu, entries):
        return {"embed": (lambda embed: [embed.add_field(name=self.name(entry), value=self.value(entry), inline=False).set_footer(icon_url=str(self.ctx.bot.user.avatar_url_as(format="png")),
                                         text=f"page {menu.current_page+1}/{self.get_max_pages()}") for entry in entries][-1])(utils.Embed(self.ctx.bot, self.ctx, **self.attrs))}


class HelpCommand(commands.HelpCommand):
    command_attrs = {"hidden": True}

    async def send_bot_help(self, mapping):
        coms = [command for commands in mapping.values() for command in commands]

        pages = menus.MenuPages(BotHelpCommand(coms, self.context, lambda command: f"{command.name} {command.signature}", lambda command: command.help.split("\n")[0], title="Commands"), clear_reactions_after=True, timeout=120)
        await pages.start(self.context)
    
    async def send_group_help(self, group):
        pages = menus.MenuPages(BotHelpCommand(list(group.commands), self.context, lambda command: f"{command.name} {command.signature}", lambda command: command.help.split("\n")[0], description=group.help+"\n\n", title=group.name), clear_reactions_after=True, timeout=120)
        await pages.start(self.context)

    async def send_command_help(self, command):
        embed = utils.Embed(self.context.bot, self.context, description=command.help, title=f"{command.name} {command.signature}")
        embed.set_footer(icon_url=str(self.context.bot.user.avatar_url_as(format="png")))
        await self.context.send(embed = embed)


def setup(bot):
    bot.help_command = HelpCommand()