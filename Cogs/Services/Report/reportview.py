from datetime import datetime

import disnake
from disnake import ButtonStyle, MessageInteraction, NotFound
from disnake.ui import button, Button


async def post_action(
    view: disnake.ui.View, interaction: MessageInteraction, action: str
):
    for child in view.children:
        child.disabled = True
    embed = interaction.message.embeds[0]
    embed.title = f"Action was taken:\n{action}"
    embed.set_footer(
        text=f"Action was taken by:\n{interaction.user.display_name}",
        icon_url=interaction.user.avatar.url,
    )
    embed.timestamp = datetime.utcnow()
    await interaction.response.edit_message(embed=embed, view=view)


class Dropdown(disnake.ui.Select):
    def __init__(self, user):
        self.user = user

        options = [
            disnake.SelectOption(
                label="10-minute timeout",
                description=f"Timeout {self.user.display_name} for ten minutes",
                emoji="🔇",
                value="10-timeout",
            ),
            disnake.SelectOption(
                label="20-minute Timeout",
                description=f"Timeout {self.user.display_name} for 20 minutes",
                emoji="🔇",
                value="20-timeout",
            ),
            disnake.SelectOption(
                label="30-minute Timeout",
                description=f"Timeout {self.user.display_name} for 30 minutes",
                emoji="🔇",
                value="30-timeout",
            ),
            disnake.SelectOption(
                label="Kick",
                description=f"Kick {self.user.display_name} from the server",
                emoji="👢",
                value="Kick",
            ),
            disnake.SelectOption(
                label="Ban",
                description=f"Ban {self.user.display_name} from the server",
                emoji="🔨",
                value="Ban",
            ),
        ]

        super().__init__(
            placeholder=f"Select the punishment for {self.user.display_name}",
            min_values=1,
            max_values=1,
            options=options,
            row=2,
        )

    async def callback(self, interaction: disnake.MessageInteraction):
        self.disabled = True

        match self.values[0]:
            case "10-timeout":
                await self.user.guild.timeout(
                    user=self.user,
                    seconds=600,
                    reason="Timed out via reported message.",
                )
                await post_action(
                    view=self.view,
                    interaction=interaction,
                    action=f"{self.user.display_name} was timed out for ten minutes."
                )
            case "20-timeout":
                await self.user.guild.timeout(
                    user=self.user,
                    seconds=1200,
                    reason="Timed out via reported message.",
                )
                await post_action(
                    view=self.view,
                    interaction=interaction,
                    action=f"{self.user.display_name} was timed out for 20 minutes."
                )
            case "30-timeout":
                await self.user.guild.timeout(
                    user=self.user,
                    seconds=18000,
                    reason="Timed out via reported message.",
                )
                await post_action(
                    view=self.view,
                    interaction=interaction,
                    action=f"{self.user.display_name} was timed out for 30 minutes."
                )
            case "Kick":
                self.placeholder = f"{self.user.display_name} was kicked"
                await post_action(
                    view=self.view,
                    interaction=interaction,
                    action=f"{self.user.display_name} was kicked",
                )
                await interaction.guild.kick(
                    user=self.user, reason="Was kicked via report"
                )
                pass
            case "Ban":
                self.placeholder = f"{self.user.display_name} was banned"
                await post_action(
                    view=self.view,
                    interaction=interaction,
                    action=f"{self.user.display_name} was banned",
                )
                await interaction.guild.ban(
                    user=self.user,
                    reason="Was banned via report",
                    delete_message_days=1,
                )
                pass


class ReportView(disnake.ui.View):
    def __init__(self, message, message_link: str):
        super().__init__(timeout=None)
        self.reported_message = message

        self.add_item(
            Button(
                label="Click here to jump to the reported message",
                url=message_link,
                row=0,
            )
        )
        self.add_item(Dropdown(message.author))

    @button(
        label="\u200b \u200b Dismiss the report",
        style=ButtonStyle.danger,
        row=1,
        custom_id="ReportButton-Dismiss",
    )
    async def dismiss_report(
        self, _button: disnake.ui.Button, interaction: disnake.MessageInteraction
    ):
        await interaction.message.delete()

    @button(
        label="\u200b \u200b Delete the message",
        style=ButtonStyle.danger,
        row=1,
        custom_id="ReportButton-DeleteMessage",
    )
    async def delete_message(
        self, _button: disnake.ui.Button, _interaction: disnake.MessageInteraction
    ):
        try:
            await post_action(
                view=self, interaction=_interaction, action="Message was deleted."
            )
            await self.reported_message.delete()
        except NotFound:
            await post_action(
                view=self,
                interaction=_interaction,
                action="Message was already deleted.",
            )
