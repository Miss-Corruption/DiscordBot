from disnake import Member
from disnake.ext.commands import Cog
from loguru import logger


class Logging(Cog, name="Logging.on_member"):
    def __init__(self, bot):
        self.bot = bot
        # logger.remove()
        member_logger = logger.bind(task="Member")
        member_logger.add(
            "../Logs/Member/{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD at HH:mm:ss} | {message}",
            rotation="500 MB",
            encoding="utf8",
        )
        self.logger = member_logger

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        self.logger.info(
            f"{member} joined the server but has not bypassed the member verification yet."
        )

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.logger.info(f"{member} left the server.")

    @Cog.listener()
    async def on_member_ban(self, member: Member) -> None:
        self.logger.info(f"{member} was banned from the server.")

    @Cog.listener()
    async def on_member_ban(self, member: Member) -> None:
        self.logger.info(f"{member} was unbanned from the server.")

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.nick != after.nick:
            self.logger.info(
                f"{before.name} has changed their nickname to: {after.nick}"
            )
        elif before.roles != after.roles:
            self.logger.info(f"{before.name}'s roles were changed to: {after.roles}")
        elif before.pending != after.pending:
            self.logger.info(f"{before.name} has finished member verification.")
