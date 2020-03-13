from . import bot, config
import argparse
import logging


passer = argparse.ArgumentParser(prog="maid", usage="python3 -m %(prog)s [options]", description="The runner for Maid bot")
passer.add_argument("--prefix", "-P", default=config.prefix, help="Overwrites the default prefix (set inside /maid/config.py)")
passer.add_argument("--debug", "-D", default="info", help="Enables logging on the bot, can be either: CRITICAL, ERROR, WARNING, INFO or DEBUG")

# TODO: add sharding impemtation
#  sharding = passer.add_argument_group("shard", "helper for running differant shard counts and ids")
#  sharding.add_argument("--shardcount", type=int, default=None)
#  sharding.add_argument("--shardids", type=int, nargs="*")

passed = passer.parse_args()

if passed.debug:
    logging.basicConfig(level=getattr(logging, passed.debug.upper()))

bot = bot.Bot(passed.prefix)

for ext in config.exts:
    bot.load_extension(ext)

bot.run(config.TOKEN)