from typing import Literal

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

from Utils.Configuration import config
from Utils.action_log import send_to_action_log


class Ban(commands.Cog, name="Ban"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="ban",
        description="Bans the given user",
        guild_ids=config.GUILD_ID,
        default_permission=False,
    )
    @commands.guild_permissions(guild_id=config.GUILD_ID[0], role_ids={}, user_ids={})
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.Member = Param(description="The Member to ban"),
        amount_of_days: Literal[0, 1, 2, 3, 4, 5, 6, 7] = Param(
            1,
            description="The amount of days to delete messages for. 1-7 days are available",
        ),
        reason: str = Param("No reason given", description="The reason for the ban"),
    ):
        try:
            await self.bot.fetch_user(member)
            return member
        except TypeError:
            pass
        ban_emb = disnake.Embed(
            title=f"Banned a member",
            description=f"{member} was banned from the server.",
            colour=0x3B1261,
        )
        ban_emb.add_field(name="Reason for ban:", value=reason)
        ban_emb.add_field(name="Was banned by:", value=inter.user.display_name)
        await member.ban(delete_message_days=amount_of_days, reason=reason)
        await send_to_action_log(inter, ban_emb)
        await inter.response.send_message(embed=ban_emb, ephemeral=True)
