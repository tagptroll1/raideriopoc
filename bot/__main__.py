import logging
import os
import sys

from bot.bot import RaiderIOBot


if __name__ == "__main__":
    log = logging.getLogger("__main__")

    token = os.getenv("RAIDERIOBOT_TOKEN")

    if not token:
        print("Missing token!")
        log.critical("Missing token, aborting startup")
        sys.exit()

    bot = RaiderIOBot(command_prefix="?")

    bot.setup_async_connector()
    bot.load_all_extensions()

    log.info("Starting bot")
    bot.run(token)
