from disnake import Activity, ActivityType, Embed
from disnake.ext.commands import Cog

from Rocchan import Rocchan


class Events(Cog, name="events.on_ready"):
    def __init__(self, bot: Rocchan):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        self.bot.main_logger.info(f"{self.bot.user.name} successfully started")

        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name=f"Eroge OST")
        )
