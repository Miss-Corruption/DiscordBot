from disnake import ApplicationCommandInteraction
from disnake.ext.commands import Cog, CommandError

from Rocchan import Rocchan


class Logging(Cog, name="on_slash_command"):
    def __init__(self, bot: Rocchan):
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
