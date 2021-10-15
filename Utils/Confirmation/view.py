import disnake


class ConfirmView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=10.0)
        self.value = None

    @disnake.ui.button(
        emoji="✅",
        style=disnake.ButtonStyle.gray,
        custom_id="ConfirmView-Yes")
    async def confirm_button(self, _, __):
        self.value = True
        self.stop()

    @disnake.ui.button(
        emoji="❌",
        style=disnake.ButtonStyle.gray,
        custom_id="ConfirmView-No")
    async def deny_button(self, _, __):
        self.value = False
        self.stop()


class DoneView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(
        label="Press this button if you're done giving yourself roles!",
        style=disnake.ButtonStyle.primary,
        custom_id="Done-Button")
    async def done_button(self, _, __):
        self.stop()
