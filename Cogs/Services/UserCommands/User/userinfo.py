import asyncio
from datetime import datetime

import disnake
from disnake import UserCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import user_command

from Utils.Configuration import config


class UserInfo(commands.Cog, name="User Info"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @user_command(
        name="User Info",
        guild_ids=config.GUILD_ID
    )
    async def user_info(self, inter: UserCommandInteraction):
        user = inter.target
        delta = f"{user.joined_at - user.created_at}"

        user_emb = disnake.Embed(
            title=f"Information about: {user.name}#{user.discriminator}",
            timestamp=datetime.utcnow(),
            colour=0x3b1261
        )
        user_emb.add_field(
            name="Current Status",
            value=user.raw_status,
            inline=True
        )
        user_emb.add_field(
            name="Current Activity",
            value=user.activity,
            inline=True
        )
        user_emb.add_field(
            name="Account created on:",
            value=user.created_at.strftime("%A, %d. %B %Y %I:%M%p"),
            inline=False
        )
        user_emb.add_field(
            name="Joined this server on:",
            value=user.joined_at.strftime("%A, %d. %B %Y %I:%M%p"),
            inline=True
        )
        user_emb.add_field(
            name="Account Delta:",
            value=f"{delta[:17]} hours",
            inline=False)

        roles = [role.mention for role in user.roles if not role.is_default()]
        role_mentions = ' '.join(roles)
        reversed(role_mentions)

        user_emb.add_field(
            name=f"{user.display_name}'s roles:",
            value=f"{role_mentions}",
            inline=True)

        user_emb.set_thumbnail(url=user.display_avatar.url)
        await inter.response.send_message(embed=user_emb)
