from disnake import Member, Embed
from disnake.ext.commands import Cog
from disnake.utils import utcnow

from Rocchan import Rocchan


class MemberLogging(Cog, name="on_member"):
    def __init__(self, bot: Rocchan):
        self.bot = bot

    @Cog.listener()
    async def on_member_join(self, member: Member) -> None:
        self.bot.join_logger.info(
            f"{member} joined the server but has not bypassed the member verification yet."
        )

        account_age = utcnow() - member.created_at

        user_emb = Embed(
            title=f"{member.name}#{member.discriminator} joined the server.",
            timestamp=utcnow(),
            colour=0x3B1261,
        )

        user_emb.set_author(
            name=f"{member.display_name}", icon_url=f"{member.display_avatar}"
        )

        user_emb.add_field(
            name="Account created on:",
            value=member.created_at.strftime("%A, %d. %B %Y %I:%M%p"),
            inline=True,
        )
        user_emb.add_field(
            name="Account Age:", value=f"{account_age[:17]} hours", inline=True
        )
        user_emb.set_footer(text=f"ID: {member.id}")
        user_emb.set_thumbnail(url=member.display_avatar.url)
        await self.bot.send_log(member, user_emb, log_type="join")

    @Cog.listener()
    async def on_member_remove(self, member: Member) -> None:
        self.bot.join_logger.info(f"{member} left the server.")
        left_emb = Embed(title=f"{member.name}#{member.discriminator} left the server.")
        left_emb.set_footer(text=f"ID: {member.id}")
        await self.bot.send_log(member, left_emb, log_type="join")

    @Cog.listener()
    async def on_member_ban(self, member: Member) -> None:
        self.bot.action_logger.warn(f"{member} was banned from the server.")

    # @Cog.listener()
    # async def on_member_update(self, before: Member, after: Member) -> None:
    #     if before.nick != after.nick:
    #         self.bot.member_logger.info(
    #             f"{before.name} has changed their nickname to: {after.nick}"
    #         )
    #     elif before.roles != after.roles:
    #         self.bot.member_logger.info(
    #             f"{before.name}'s roles were changed to: {after.roles}"
    #         )
    #     elif before.pending != after.pending:
    #         self.bot.member_logger.info(
    #             f"{before.name} has finished member verification."
    #         )
