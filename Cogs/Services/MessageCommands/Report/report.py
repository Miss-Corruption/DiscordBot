import asyncio
from datetime import datetime

import disnake
from disnake import MessageCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import message_command

from Utils.Configuration import config
from Utils.Confirmation.view import ConfirmView


class MessageLink(disnake.ui.View):
    def __init__(self, message_link: str):
        super().__init__()
        self.add_item(
            disnake.ui.Button(
                label='Click here to jump to the reported message',
                url=message_link
            )
        )


class ReportMessage(commands.Cog, name="ReportMessage"):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def confirm_report(ctx):
        view = ConfirmView()

        confirm_emb = disnake.Embed(
            title="Confirmation needed",
            description="Would you like to report this message? This will ping moderators, and false "
                        "reporting will be treated as spam and punished accordingly.",
            colour=0x3b1261
        )

        cancel_emb = disnake.Embed(
            title="Report cancelled",
            description="The report has been cancelled.",
            colour=0x3b1261
        )

        thank_emb = disnake.Embed(
            title="Message reported!",
            description="Thank you for your report.",
            colour=0x3b1261
        )

        timeout_emb = disnake.Embed(
            title="Timed out!",
            description="The report has timed out, cancelling...",
            colour=0x3b1261
        )

        await ctx.response.send_message(
            embed=confirm_emb,
            view=view
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
            await ctx.edit_original_message(embed=thank_emb, view=None)
            await asyncio.sleep(3)
            await ctx.delete_original_message()
            return True
        else:
            await ctx.edit_original_message(embed=cancel_emb, view=None)
            await asyncio.sleep(3)
            await ctx.delete_original_message()
            return False

    @message_command(
        name="Report Message",
        guild_ids=config.GUILD_ID
    )
    async def report_message(self, inter: MessageCommandInteraction):

        conf = await self.confirm_report(inter)
        if not conf:
            return

        match inter.target.embeds:
            case []:
                match inter.target.attachments:
                    case []:
                        report_emb = disnake.Embed(
                            title="Message reported",
                            description=f"A message was reported in: {inter.target.channel.mention}",
                            timestamp=datetime.utcnow(),
                            colour=0x3b1261
                        )
                        report_emb.add_field(
                            name=f"Message Content:",
                            value=f"{inter.target.content}",
                            inline=False
                        )
                        report_emb.add_field(
                            name="Message was written by:",
                            value=f"{inter.target.author.mention}",
                        )
                        report_emb.set_footer(
                            text=f"Message reported by: {inter.user.display_name}",
                            icon_url=inter.user.avatar.url
                        )
                        await inter.guild.get_channel(config.ACTION_LOG).send(
                            embed=report_emb,
                            view=MessageLink(inter.target.jump_url))
                    case _:
                        report_emb = disnake.Embed(
                            title="Image reported",
                            description=f"An image was reported in: {inter.target.channel.mention}",
                            timestamp=datetime.utcnow(),
                            colour=0x3b1261
                        )
                        image = inter.target.attachments[0]
                        report_emb.set_image(url=image.url)

                        report_emb.add_field(
                            name="Image was sent by:",
                            value=f"{inter.target.author.mention}",
                        )

                        report_emb.set_footer(
                            text=f"Image reported by: {inter.user.display_name}",
                            icon_url=inter.user.avatar.url
                        )

                        await inter.guild.get_channel(config.ACTION_LOG).send(
                            embed=report_emb,
                            view=MessageLink(inter.target.jump_url))

            case _:
                report_emb = disnake.Embed(
                    title="Embed reported",
                    description=f"An embed was reported in: {inter.target.channel.mention}",
                    timestamp=datetime.utcnow(),
                    colour=0x3b1261
                )

                report_emb.add_field(
                    name="Embed was sent by:",
                    value=f"{inter.target.author.mention}",
                )

                report_emb.set_footer(
                    text=f"Embed reported by: {inter.user.display_name}",
                    icon_url=inter.user.avatar.url
                )

                await inter.guild.get_channel(config.ACTION_LOG).send(
                    embed=report_emb,
                    view=MessageLink(inter.target.jump_url))
