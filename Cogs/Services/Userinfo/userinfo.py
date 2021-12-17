import textwrap
from datetime import datetime

import disnake
from disnake import UserCommandInteraction, ActivityType
from disnake.ext import commands
from disnake.ext.commands import user_command

from Utils.Configuration import config


class UserInfo(commands.Cog, name="User Info"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @user_command(name="User Info", guild_ids=config.GUILD_ID)
    async def user_info(self, inter: UserCommandInteraction):
        user = await inter.guild.getch_member(inter.target.id, strict=True)
        delta = f"{user.joined_at - user.created_at}"

        user_emb = disnake.Embed(
            title=f"Information about:\n{user.name}#{user.discriminator}",
            timestamp=datetime.utcnow(),
            colour=0x3B1261,
        )

        user_emb.set_author(
            name=f"{user.display_name}", icon_url=f"{user.display_avatar}"
        )

        user_emb.add_field(
            name="Account created on:",
            value=user.created_at.strftime("%A, %d. %B %Y %I:%M%p"),
            inline=True,
        )
        user_emb.add_field(
            name="Joined this server on:",
            value=user.joined_at.strftime("%A, %d. %B %Y %I:%M%p"),
            inline=True,
        )
        user_emb.add_field(
            name="Account Delta:", value=f"{delta[:17]} hours", inline=True
        )

        user_emb.add_field(name="Current Status", value=user.raw_status, inline=True)
        act_type = ""
        if user.activity:
            match user.activity.type:
                case ActivityType.listening:
                    act_type = "Listening to: "
                case ActivityType.playing:
                    act_type = "Currently playing: "
                case ActivityType.streaming:
                    act_type = "Currently streaming: "
                case ActivityType.watching:
                    act_type = "Currently watching: "
            user_emb.add_field(
                name="Current Activity",
                value=f"{act_type}{user.activity.name}",
                inline=True,
            )
        user_emb.add_field(name="\u200b", value=f"\u200b", inline=True)

        roles = [role.mention for role in user.roles if not role.is_default() and role]
        rev_roles = reversed(roles)
        role_mentions = " ".join(rev_roles)

        user_emb.add_field(
            name=f"{user.display_name}'s roles:", value=f"{role_mentions}", inline=False
        )
        user_emb.set_footer(text=f"ID: {user.id}")
        user_emb.set_thumbnail(url=user.display_avatar.url)
        await inter.response.send_message(embed=user_emb)
