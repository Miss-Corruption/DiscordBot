import os
import sys
import traceback

from disnake import ApplicationCommandInteraction, OptionType
from disnake.ext.commands import Cog, CommandError
from loguru import logger


class Logging(Cog, name="Logging.on_slash_command"):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def add_traceback(record):
        extra = record["extra"]
        if extra.get("with_traceback", False):
            extra["traceback"] = "\n" + "".join(traceback.format_stack())
        else:
            extra["traceback"] = ""

    @Cog.listener()
    async def on_slash_command_completion(
        self, interaction: ApplicationCommandInteraction
    ) -> None:
        cmd_name = interaction.data.name
        options = bool(interaction.data.options)
        data = interaction.data

        while options:
            data = data.options[0]

            if data.type not in (OptionType.sub_command_group, OptionType.sub_command):
                options = False
                continue

            cmd_name += f" {data.name}"

            if not data.options:
                options = False
        self.bot.slash_command_logger.info(
            f"{interaction.author.display_name} used {cmd_name}."
        )

    @Cog.listener()
    async def on_slash_command_error(
        self, interaction: ApplicationCommandInteraction, error: CommandError
    ) -> None:
        self.bot.slash_command_logger = self.bot.slash_command_logger.patch(
            self.add_traceback
        )
        self.bot.slash_command_logger.add(
            sys.stderr, format="{time} - {message}{extra[traceback]}"
        )

        self.bot.slash_command_logger.bind(with_traceback=True).exception(
            f"Failed to execute {interaction.data.name}:\n"
            f"Error: {error}\n"
            f"Traceback:\n"
        )
