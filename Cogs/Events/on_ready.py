from logging import info

from disnake import Activity, ActivityType
from disnake.ext.commands import Cog

from Bot import Rocchan


class Events(Cog, name="events.on_ready"):
    def __init__(self, bot: Rocchan):
        self.bot = bot

    @Cog.listener()
    async def on_ready(self):
        info("Rocchan successfully started")

        await self.bot.change_presence(
            activity=Activity(type=ActivityType.listening, name=f"Eroge OST")
        )

        self.bot.starting = False
