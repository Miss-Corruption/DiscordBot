import traceback
from typing import Any, Literal

import aiohttp
import disnake
from disnake import Intents
from disnake.ext.commands import Bot, Context
from loguru import logger

from Data import Database

__all__ = ["Rocchan"]


class Rocchan(Bot):
    help_command: Literal[None] = None

    def __init__(self, prefix: str, **kwargs: Any):
        super().__init__(
            prefix,
            intents=self.get_intents(),
            sync_commands_debug=True,
            sync_permissions=True,
            **kwargs,
        )

        self.loop.run_until_complete(Database.init())
        self.http_session = aiohttp.ClientSession(loop=self.loop)

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        user_id, created_at, hmac = disnake.utils.parse_token(token)
        # try:
        #     # await Database.init()
        #     logger.info("Database initialized")
        # except Exception:
        #     print(traceback.format_exc())
        logger.info("Bot was started")

    def load_extensions(self, cogs: Context = None, path: str = "Cogs."):
        """Loads the default set of extensions or a seperate one if given"""
        for extension in cogs or self._extensions:
            try:
                self.load_extension(f"{path}{extension}")
                print(f"Loaded cog: {extension}")
            except Exception as e:
                logger.error(f"LoadError: {extension}\n" f"{type(e).__name__}: {e}")
        logger.info("All cogs loaded")

    @staticmethod
    def get_intents():
        """Configure the intents for the bot"""
        intents = Intents(
            guilds=True,
            guild_messages=True,
            guild_reactions=True,
            members=True,
            presences=True,
        )
        return intents
