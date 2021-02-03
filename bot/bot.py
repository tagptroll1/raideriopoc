import logging
import socket
from typing import Optional

from aiohttp import AsyncResolver, ClientSession, TCPConnector
from discord import Intents
from discord.ext.commands import Bot


log = logging.getLogger("bot")
EXTENSIONS = [
    "bot.cogs.raiderio",
    "bot.cogs.bot",
]


class RaiderIOBot(Bot):
    """Discord.py bot for interacting with the Raider.io api"""

    def __init__(self, *args, **kwargs):
        intents = Intents.all()
        intents.presences = False
        intents.dm_typing = False
        intents.dm_reactions = False
        intents.invites = False
        intents.webhooks = False
        intents.integrations = False

        kwargs["intents"] = intents

        super().__init__(*args, **kwargs)

        self.http_session: Optional[ClientSession] = None
        self._connector = None
        self._resolver = None

    def load_all_extensions(self) -> None:
        """Load all extensions"""
        for extension in EXTENSIONS:
            try:
                self.load_extension(extension)
                print(f"Loading... {extension:<22} Success!")
                log.info(f"Loading... {extension:<22} Success!")
            except Exception as e:
                log.exception(f"\nLoading... {extension:<22} Failed!")
                print("-"*25)
                print(f"Loading... {extension:<22} Failed!")
                print(e, "\n", "-"*25, "\n")

    async def close(self) -> None:
        await super().close()

        if self.http_session:
            await self.http_session.close()

    def setup_async_connector(self):
        # Use asyncio for DNS resolution instead of threads
        # so threads aren't spammed.
        self._resolver = AsyncResolver()

        # Use AF_INET as its socket family to prevent HTTPS related problems
        self._connector = TCPConnector(
            resolver=self._resolver,
            family=socket.AF_INET,
        )

        # Client.login() will call HTTPClient.static_login()
        # which will create a session using
        # this connector attribute.
        self.http.connector = self._connector
        self.http_session = ClientSession(connector=self._connector)
