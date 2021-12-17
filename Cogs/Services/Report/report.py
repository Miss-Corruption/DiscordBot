from datetime import datetime

import disnake
from disnake import MessageCommandInteraction, Embed, MessageInteraction
from disnake.ext import commands
from disnake.ext.commands import message_command

from Utils.Configuration import config
from Utils.Views import Confirm
from .reportview import ReportView


class ReportMessage(commands.Cog, name="ReportMessage"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    async def confirm_report(ctx):

        confirm_emb = disnake.Embed(
            title="Confirmation needed",
            description="Would you like to report this message? This will ping moderators, and false "
            "reporting will be treated as spam and punished accordingly.",
            colour=0x3B1261,
        )

        cancel_emb = disnake.Embed(
            title="Report cancelled",
            description="The report has been cancelled.",
            colour=0x3B1261,
        )

        thank_emb = disnake.Embed(
            title="Message reported!",
            description="Thank you for your report.",
            colour=0x3B1261,
        )

        async def callback(value, interaction: MessageInteraction):
            if not value:
                return (
                    await interaction.response.edit_message(
                        embed=cancel_emb, view=None
                    ),
                )
            if value:
                return (
                    await interaction.response.edit_message(embed=thank_emb, view=None),
                )

        view = Confirm(callback, listen_to=(ctx.author.id,))
        await ctx.send(embed=confirm_emb, view=view, ephemeral=True)

        await view.wait()
        return view.value

    @message_command(name="Report Message", guild_ids=config.GUILD_ID)
    async def report_message(self, inter: MessageCommandInteraction):

        conf = await self.confirm_report(inter)
        if not conf:
            return

        match inter.target.embeds:
            case []:
                report_emb = Embed(
                    title="Message reported",
                    description=f"A message was reported in: {inter.target.channel.mention}",
                    timestamp=datetime.utcnow(),
                    color=0x3B1261,
                )

                report_emb.set_author(
                    name=f"Message reported by:\n{inter.user.display_name}",
                    icon_url=inter.user.avatar.url,
                )

                if inter.target.content:
                    report_emb.add_field(
                        name=f"Message Content:",
                        value=f"{inter.target.content}",
                        inline=False,
                    )

                report_emb.add_field(
                    name="Message was written by:",
                    value=f"{inter.target.author.mention}",
                )

                if inter.target.attachments:
                    image = inter.target.attachments[0]
                    report_emb.add_field(
                        name=f"Message Attachment:", value="\u200b", inline=False
                    )
                    report_emb.set_image(url=image.url)

                report_emb.set_footer(text="No action was taken yet.")

                await inter.guild.get_channel(config.ACTION_LOG).send(
                    embed=report_emb,
                    view=ReportView(inter.target, inter.target.jump_url),
                )

            case _:
                report_emb = disnake.Embed(
                    title="Embed reported",
                    description=f"An embed was reported in: {inter.target.channel.mention}",
                    timestamp=datetime.utcnow(),
                    colour=0x3B1261,
                )

                report_emb.set_author(
                    name=f"Message reported by:\n{inter.user.display_name}",
                    icon_url=inter.user.avatar.url,
                )

                report_emb.add_field(
                    name="Embed was sent by:",
                    value=f"{inter.target.author.mention}",
                )

                await inter.guild.get_channel(config.ACTION_LOG).send(
                    embed=report_emb,
                    view=ReportView(inter.target, inter.target.jump_url),
                )
