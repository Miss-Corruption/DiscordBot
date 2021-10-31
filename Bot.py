import importlib
import logging
import os
import traceback
from asyncio import get_event_loop_policy
from datetime import date
from logging import basicConfig, DEBUG
from pathlib import Path

from disnake import Intents
from disnake.ext.commands import Bot, ExtensionFailed

from Utils.Configuration import config
from Data import Database as db


class Rocchan(Bot):
    def __init__(self, **kwargs):
        """Initialize the bot"""
        super().__init__(
            command_prefix=config.PREFIX,
            intents=self.get_intents(),
            help_command=None,
            case_insensitive=True,
            strip_after_prefix=True,
            sync_commands_debug=True,
            sync_permissions=True,
            **kwargs,
        )

        for module_path in Path("Cogs").rglob("*.py"):
            # convert 'dir1/dir2/file.py' to 'dir1.dir2.file'
            module_name = str(module_path).removesuffix(".py").replace(os.path.sep, ".")
            # import module, check if `setup` method exists
            module = importlib.import_module(module_name)
            if hasattr(module, "setup"):
                try:
                    self.load_extension(module_name)
                    logging.debug(f"Loaded extension: {module_name[5:-9]}")
                    print(f"Loaded extension: {module_name[5:-9]}")
                except ExtensionFailed:
                    logging.error(
                        f"Failed to load the following extension: {module_name[5:-9]}.\n"
                        + f"--------------------------------------------------------\n"
                        + traceback.format_exc()
                        + f"--------------------------------------------------------"
                    )

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

    @classmethod
    async def setup(self, **kwargs):
        """Setup the bot with a token from data.constants or the .env file"""
        bot = self()
        try:
            await db.init()
            await bot.start(config.BOT_TOKEN, **kwargs)
        except KeyboardInterrupt:
            await bot.close()


if __name__ == "__main__":

    if not os.path.exists("logs"):  # Create logs folder if it doesn't exist
        os.makedirs("logs")

    basicConfig(
        filename=f"logs/{date.today().strftime('%d-%m-%Y_')}app.log",
        filemode="a",
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d-%m-%y %H:%M:%S",
        level=DEBUG,
    )

    os.system("cls" if os.name == "nt" else "clear")
    print("Bot is starting...")
    loop = get_event_loop_policy().get_event_loop()
    try:
        loop.run_until_complete(Rocchan.setup())  # Starts the bot
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(e)
