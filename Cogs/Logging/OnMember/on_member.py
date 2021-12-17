from disnake import Member
from disnake.ext.commands import Cog

from Rocchan import Rocchan


class MemberLogging(Cog, name="Logging.on_member"):
    def __init__(self, bot: Rocchan):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        self.bot.member_logger.info(
            f"{member} joined the server but has not bypassed the member verification yet."
        )

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.bot.member_logger.info(f"{member} left the server.")

    @Cog.listener()
    async def on_member_ban(self, member: Member) -> None:
        self.bot.member_logger.warn(f"{member} was banned from the server.")

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        if before.nick != after.nick:
            self.bot.member_logger.info(
                f"{before.name} has changed their nickname to: {after.nick}"
            )
        elif before.roles != after.roles:
            self.bot.member_logger.info(
                f"{before.name}'s roles were changed to: {after.roles}"
            )
        elif before.pending != after.pending:
            self.bot.member_logger.info(
                f"{before.name} has finished member verification."
            )
