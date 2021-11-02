from disnake import Activity, ActivityType
from disnake.ext.commands import Cog
from loguru import logger


class Events(Cog, name="events.on_ready"):
    def __init__(self, bot):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        logger.info(f"{self.bot.user.name} successfully started")

        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name=f"Eroge OST")
        )

        self.bot.starting = False
