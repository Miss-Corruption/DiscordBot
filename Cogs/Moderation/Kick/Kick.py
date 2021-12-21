import os

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param
from dotenv import load_dotenv

from Rocchan import Rocchan

load_dotenv()


class Kick(commands.Cog, name="Kick"):
    GUILD_ID = [int(os.environ["GUILD_ID"])]

    def __init__(self, bot: Rocchan):
        self.bot = bot

    @commands.slash_command(
        name="ping", description="Kicks the given user", guild_ids=GUILD_ID
    )
    async def ping(
        self,
        inter: disnake.ApplicationCommandInteraction,
    ):
        await inter.response.send_message("Pong")

    @commands.slash_command(
        name="kick", description="Kicks the given user", guild_ids=GUILD_ID
    )
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        inter: disnake.ApplicationCommandInteraction,
        member: disnake.User = Param(description="The User to kick"),
        reason: str = Param("No reason given", description="The reason for the kick"),
    ):
        kick_emb = disnake.Embed(
            title=f"Kicked a member",
            description=f"{member} was kicked from the server.",
            colour=0x3B1261,
        )
        kick_emb.add_field(name="Reason for kick:", value=reason)
        kick_emb.add_field(name="Was kicked by:", value=inter.user.display_name)
        await inter.guild.kick(member, reason=reason)
        self.bot.action_logger.warn(f"f{inter.user} has kicked {member}")
        await inter.response.send_message(embed=kick_emb, ephemeral=True)


def setup(bot):
    bot.add_cog(Kick(bot))
