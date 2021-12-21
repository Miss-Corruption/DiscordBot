import os
from typing import Literal

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from dotenv import load_dotenv

from Rocchan import Rocchan

load_dotenv()


class Ban(commands.Cog, name="Ban"):
    GUILD_ID = [int(os.environ["GUILD_ID"])]

    def __init__(self, bot: Rocchan):
        self.bot = bot

    @commands.slash_command(
        name="ban", description="Bans the given user", guild_ids=GUILD_ID
    )
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.User = Param(description="The Member to ban"),
        amount_of_days: Literal[0, 1, 2, 3, 4, 5, 6, 7] = Param(
            1,
            description="The amount of days to delete messages for. 1-7 days are available",
        ),
        reason: str = Param("No reason given", description="The reason for the ban"),
    ):
        ban_emb = disnake.Embed(
            title=f"Banned a member",
            description=f"{member} was banned from the server.",
            colour=0x3B1261,
        )
        ban_emb.add_field(name="Reason for ban:", value=reason)
        ban_emb.add_field(name="Was banned by:", value=inter.user.display_name)
        await inter.guild.ban(member, delete_message_days=amount_of_days, reason=reason)
        self.bot.action_logger.warning(f"{inter.user} has banned {member}")
        await inter.response.send_message(embed=ban_emb, ephemeral=True)
