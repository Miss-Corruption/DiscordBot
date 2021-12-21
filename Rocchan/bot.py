import os
import traceback
from itertools import takewhile
from typing import Any, Literal

import aiohttp
import disnake
from disnake import Intents, Member, Embed
from disnake.ext.commands import Bot, Context, errors
from dotenv import load_dotenv
from loguru import logger

from Data import Database

__all__ = ["Rocchan"]

load_dotenv()


def make_filter(name):
    def filter(record):
        return record["extra"].get("name") == name

    return filter


def tracing_formatter(record):
    # Filter out frames coming from Loguru internals
    frames = takewhile(
        lambda f: "/loguru/" not in f.filename, traceback.extract_stack()
    )
    stack = " > ".join("{}:{}:{}".format(f.filename, f.name, f.lineno) for f in frames)
    record["extra"]["stack"] = stack
    return "{level} | {extra[stack]} - {message}\n{exception}"


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
    "../Logs/SlashCommands/Log_{time:YYYY-MM-DD}.log",
    format=tracing_formatter,
    rotation="12:00",
    compression="zip",
    filter=make_filter("slash"),
)


class Rocchan(Bot):
    main_logger = logger.bind(name="main")
    slash_command_logger = logger.bind(name="slashcmd")
    action_logger = logger.bind(name="action")
    messages_logger = logger.bind(name="messages")
    join_logger = logger.bind(name="join")
    message_channel = int(os.environ["MESSAGE_CHANNEL"])
    action_channel = int(os.environ["ACTION_CHANNEL"])
    join_channel = int(os.environ["JOIN_CHANNEL"])
    help_command: Literal[None] = None

    @classmethod
    async def send_log(
        cls,
        member: Member,
        embed: Embed,
        log_type: Literal["join", "action", "message"],
    ):
        channels = {
            "join": cls.join_channel,
            "message": cls.message_channel,
            "action": cls.action_channel,
        }
        channel = member.guild.get_channel(channels[log_type])
        await channel.send(embed=embed)

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

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        user_id, created_at, hmac = disnake.utils.parse_token(token)
        self.main_logger.info(f"START [ID: {user_id}]")
        return await super().start(token, reconnect=reconnect)

    async def on_command_error(self, context: Context, exception: errors.CommandError) -> None:
        match exception:
            case errors.CommandNotFound:
                print("Not found")
            case errors.CommandOnCooldown:
                print("Cooldown")
            case errors.DisabledCommand:
                print("Disabled")
