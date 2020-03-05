"""Config data for Maid."""
import random

TOKEN = "token here"
prefix = "!"
database_config = dict(user="username", database="database name", host="host here", password="password here")

# all this can be changed theys are just examples

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

allowed_attrs_names = [
    r"{{content}}",
    r"{{author_mention}}",
    r"{{author_name}}",
    r"{{author_discriminator}}" ,
    r"{{owner_mention}}",
    r"{{owner_name}}",
    r"{{owner_discriminator}}",
]
special_names = [
    r"{{random(1, 2, 3, ...)}}",
]