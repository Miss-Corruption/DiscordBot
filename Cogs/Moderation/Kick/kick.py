import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

import Utils
from Utils.Mod.action_log import send_to_action_log


class Kick(commands.Cog, name="Kick"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command(
        name="kick",
        description="Kicks the given user",
        guild_ids=Utils.Configuration.GUILD_ID
    )
    @commands.bot_has_permissions(kick_members=True)
    async def kick(
            self,
            inter: disnake.ApplicationCommandInteraction,
            member: disnake.Member = Param(
                description="The User to kick"
            ),
            reason: str = Param(
                "No reason given",
                description="The reason for the kick"
            )
    ):
        kick_emb = disnake.Embed(
            title=f"Kicked a member",
            description=f"{member} was kicked from the server.",
            colour=0x3b1261
        )
        kick_emb.add_field(
            name="Reason for kick:",
            value=reason
        )
        kick_emb.add_field(
            name="Was kicked by:",
            value=inter.user.display_name
        )
        await member.kick(reason=reason)
        await send_to_action_log(inter, kick_emb)
        await inter.response.send_message(embed=kick_emb, ephemeral=True)
