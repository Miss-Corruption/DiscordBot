import asyncio
from datetime import datetime, timedelta, timezone
from typing import Callable, List, Optional, Union

import disnake
from disnake.ext import commands
from disnake.ext.commands import Param

from Utils.Configuration import config
from Utils.Confirmation.view import ConfirmView
from Utils.Mod import permissions
from Utils.Mod.cleanup import mass_purge


class Purge(commands.Cog, name="Purge"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def confirm_100_plus_deletions(ctx: disnake.ApplicationCommandInteraction, number: int):
        view = ConfirmView()
        await ctx.response.send_message(
            f"Do you want to delete {number} amount of messages?",
            view=view
        )

        timeout_emb = disnake.Embed(
            title="Timed out!",
            description="The report has timed out, cancelling...",
            colour=0x3b1261
        )

        await view.wait()
        if view.timeout:
            await ctx.edit_original_message(embed=timeout_emb, view=None)
            await asyncio.sleep(3)
            await ctx.delete_original_message()
            return False

        if view.value is None:
            return
        elif view.value:
            view.clear_items()
            await ctx.delete_original_message()
            return True
        else:
            view.clear_items()
            await ctx.delete_original_message()
            return False

    @staticmethod
    async def get_messages_for_deletion(
            *,
            channel: Union[disnake.TextChannel, disnake.DMChannel],
            amount: Optional[int] = None,
            check: Callable[[disnake.Message], bool] = lambda x: True,
            limit: Optional[int] = None,
            before: Union[disnake.Message, datetime] = None,
            after: Union[disnake.Message, datetime] = None,
            delete_pinned: bool = False,
    ) -> List[disnake.Message]:

        two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14, minutes=-5)

        def message_filter(messages):

            return (
                    check(messages)
                    and messages.created_at > two_weeks_ago
                    and (delete_pinned or not messages.pinned)
            )

        if after:
            if isinstance(after, disnake.Message):
                after = after.created_at
            after = max(after, two_weeks_ago)

        collected = []
        async for message in channel.history(
                limit=limit, before=before, after=after, oldest_first=False
        ):
            if message.created_at < two_weeks_ago:
                break
            if message_filter(message):
                collected.append(message)
                if amount is not None and amount <= len(collected):
                    break

        return collected

    @staticmethod
    async def get_message_from_reference(
            channel: disnake.TextChannel, reference: disnake.MessageReference
    ) -> Optional[disnake.Message]:
        resolved = reference.resolved
        if resolved and isinstance(resolved, disnake.Message):
            message = resolved
        elif message := reference.cached_message:
            pass
        else:
            try:
                message = await channel.fetch_message(reference.message_id)
            except disnake.NotFound:
                pass
        return message

    @commands.slash_command(
        name="purge",
        guild_ids=config.GUILD_ID,
    )
    @permissions.require(
        user_ids={210887957723348993: True}
    )
    @commands.bot_has_permissions(manage_messages=True)
    async def purge(self, inter: disnake.ApplicationCommandInteraction):
        inter.response.defer(ephemeral=True)
        pass

    @purge.sub_command(
        name="messages",
        description="Deletes given amount of messages",
    )
    async def messages(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            amount: int = Param(
                description="The amount of messages to delete"
            ),
            delete_pinned: bool = Param(
                False, description="Should pinned messages be deleted?"
            ),
    ):
        channel = ctx.guild.get_channel_or_thread(ctx.channel_id)
        message = await ctx.original_message()

        if amount > 100:
            cont = await self.confirm_100_plus_deletions(ctx, amount)
            if not cont:
                return

        to_delete = await self.get_messages_for_deletion(
            channel=channel, amount=amount, before=message, delete_pinned=delete_pinned
        )
        await mass_purge(to_delete, channel)
        await ctx.edit_original_message(
            content=f"Deleted {len(to_delete)} messages in {channel.mention}"
        )

    @purge.sub_command(
        name="user",
        description="Delete the messages from the given user",
    )
    async def user(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            user: Union[disnake.User] = Param(
                description="The user to delete messages from"
            ),
            amount: int = Param(
                description="The amount of messages to delete from the given user"
            ),
            delete_pinned: bool = Param(
                False, description="Should pinned messages be deleted?"
            ),
    ):
        channel = ctx.guild.get_channel_or_thread(ctx.channel_id)
        message = await ctx.original_message()
        _id = user.id

        if amount > 100:
            cont = await self.confirm_100_plus_deletions(ctx, amount)
            if not cont:
                return

        def check(m):
            if m.author.id == _id:
                return True
            else:
                return False

        to_delete = await self.get_messages_for_deletion(
            channel=channel,
            amount=amount,
            check=check,
            before=message,
            delete_pinned=delete_pinned,
        )
        await mass_purge(to_delete, channel)
        await ctx.edit_original_message(
            content=f"Deleted {amount} messages from {user.mention}"
        )

    @purge.sub_command(
        name="before",
        description="Deletes given number of messages before the given message",
    )
    async def before(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            message: str = Param(
                description="Message to start deleting from"
            ),
            amount: int = Param(
                description="The amount of messages to delete from the given user"
            ),
            delete_pinned: bool = Param(
                False, description="Should pinned messages be deleted?"
            ),
    ):
        channel = ctx.guild.get_channel_or_thread(ctx.channel_id)

        try:
            before = await channel.fetch_message(int(message))
        except disnake.NotFound:
            return await ctx.response.send_message("Message not found! :c", ephemeral=True)

        to_delete = await self.get_messages_for_deletion(
            channel=channel, amount=amount, before=before, delete_pinned=delete_pinned
        )
        await mass_purge(to_delete, channel)
        await ctx.edit_original_message(
            content=f"Deleted {len(to_delete)} messages in {channel.mention}"
        )

    @purge.sub_command(
        name="after",
        description="Deletes all messages after the given message",
    )
    async def after(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            message: str = Param(
                description="Message ID to start deleting from"
            ),
            delete_pinned: bool = Param(
                False, description="Should pinned messages be deleted?"
            ),
    ):
        channel = ctx.guild.get_channel_or_thread(ctx.channel_id)

        try:
            after = await channel.fetch_message(int(message))
        except disnake.NotFound:
            return await ctx.response.send_message("Message not found! :c", ephemeral=True)

        to_delete = await self.get_messages_for_deletion(
            channel=channel, amount=None, after=after, delete_pinned=delete_pinned
        )
        await mass_purge(to_delete, channel)
        await ctx.edit_original_message(
            content=f"Deleted {len(to_delete)} messages in {channel.mention}"
        )

    @purge.error
    async def purge_error(self, ctx, error):
        if isinstance(error, commands.errors.BotMissingPermissions):
            miss_perms = disnake.Embed(
                title="Missing Permission!",
                description=f"{self.bot.user.display_name} needs the \"Manage Messages\" permission.",
                colour=0x3b1261
            )
            await ctx.response.send_message(embed=miss_perms)
