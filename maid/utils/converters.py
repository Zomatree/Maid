from discord.ext import commands


class ExcludedCommand(commands.CheckFailure):
    name = None


class NoCommandFound(commands.CheckFailure):
    name = None


class CommandConverter(commands.Converter):
    def __init__(self, exclude: list=[]):
        self.exclude = exclude

    async def convert(self, ctx, name):
        if name in self.exclude:
            error = ExcludedCommand()
            error.name = name
            raise error
        command = ctx.bot.get_command(name)
        if not command:
            error = NoCommandFound()
            error.name = name
            raise error
        return command
