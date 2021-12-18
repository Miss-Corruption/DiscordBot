import os
import sys
import traceback

from disnake import ApplicationCommandInteraction, OptionType
from disnake.ext.commands import Cog, CommandError
from loguru import logger


class Logging(Cog, name="Logging.on_slash_command"):
    def __init__(self, bot):
        self.bot = bot

    from disnake import ApplicationCommandInteraction, OptionType
    from disnake.ext.commands import Cog, CommandError

    class Logging(Cog, name="Logging.on_slash_command"):
        def __init__(self, bot):
            self.bot = bot

        @Cog.listener()
        async def on_slash_command_completion(
            self, interaction: ApplicationCommandInteraction
        ) -> None:
            self.bot.slash_command_logger.info(
                f"{interaction.author.display_name} invoked {interaction.application_command.qualified_name} "
                f"{interaction.filled_options} in {interaction.channel}."
            )

        @Cog.listener()
        async def on_slash_command_error(
            self, interaction: ApplicationCommandInteraction, error: CommandError
        ) -> None:
            self.bot.slash_command_logger.exception(
                f"Exception in: {interaction.application_command.qualified_name}"
                f"\nError: {error}"
                f"\nTraceback:"
            )
