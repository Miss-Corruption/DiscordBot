from typing import Any, Literal

import aiohttp
import disnake
from disnake import Intents
from disnake.ext.commands import Bot, Context
from loguru import logger

from Data import Database

__all__ = ["Rocchan"]


def make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name

    return filter


logger.add(
    "../Logs/Bot/Log_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="12:00",
    compression="zip",
    filter=make_filter("main"),
)

logger.add(
    "../Logs/Action/Log_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="12:00",
    compression="zip",
    filter=make_filter("action"),
)

logger.add(
    "../Logs/Messages/Log_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="12:00",
    compression="zip",
    filter=make_filter("messages"),
)

logger.add(
    "../Logs/Members/Log_{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="12:00",
    compression="zip",
    filter=make_filter("members"),
)

logger.add(
    "../Logs/SlashCommands/{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="500 MB",
    backtrace=True,
    diagnose=True,
    level="TRACE",
    filter=make_filter("slashcmd"),
)


class Rocchan(Bot):
    main_logger = logger.bind(name="main")
    action_logger = logger.bind(name="action")
    messages_logger = logger.bind(name="messages")
    member_logger = logger.bind(name="members")
    slash_command_logger = logger.bind(name="slashcmd")
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
        self.main_logger.info(f"START [ID: {user_id}]")
        return await super().start(token, reconnect=reconnect)

    def load_extensions(self, cogs: Context = None, path: str = "Cogs."):
        """Loads the default set of extensions or a seperate one if given"""
        for extension in cogs or self._extensions:
            try:
                self.load_extension(f"{path}{extension}")
                self.main_logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                self.main_logger.exception(
                    f"LoadError: {extension}\n" f"{type(e).__name__}: {e}"
                )
        self.main_logger.info("All cogs loaded")

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
