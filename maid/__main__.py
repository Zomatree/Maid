from . import bot, config
import argparse
import logging


passer = argparse.ArgumentParser(prog="maid", usage="python3 -m %(prog)s [options]", description="The runner for Maid bot")
passer.add_argument("--prefix", "-P", default=config.prefix, help="Overwrites the default prefix (set inside /maid/config.py)")
passer.add_argument("--debug", "-D", default=False, action="store_true", help="Enables logging on the bot ")

# TODO: add sharding impemtation
#  sharding = passer.add_argument_group("shard", "helper for running differant shard counts and ids")
#  sharding.add_argument("--shardcount", type=int, default=None)
#  sharding.add_argument("--shardids", type=int, nargs="*")

passed = passer.parse_args()

if passed.debug:
    logging.basicConfig(level=logging.INFO)

bot = bot.Bot(passed.prefix)

bot.run(config.TOKEN)