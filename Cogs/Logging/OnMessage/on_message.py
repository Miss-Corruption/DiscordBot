from disnake import Message, Embed
from disnake.ext.commands import Cog

from Rocchan import Rocchan


class MessageLogging(Cog, name="Logging.on_message"):
    def __init__(self, bot: Rocchan):
        self.bot = bot

    @Cog.listener()
    async def on_message_edit(self, message: Message, after):
        if message.content != after.content:
            self.bot.messages_logger.info(
                f"{message.author} edited his message./n"
                f"Before: {message.content}\n"
                f"After: {after.content}"
            )
            edit_emb = Embed(
                title=f"{message.author} edited their message", color=0x3B1261
            )
            edit_emb.add_field(name="Before:", value=f"{message.content}")
            edit_emb.add_field(name="After:", value=f"{after.content}")
            channel = message.guild.get_channel(int(self.log_channel))
            await channel.send(embed=edit_emb)

    @Cog.listener()
    async def on_message_delete(self, message: Message):
        self.bot.messages_logger.warn(
            f"The following message got deleted in {message.channel}: {message.content}"
        )
        del_emb = Embed(title="Message got deleted", colour=0x3B1261)
        del_emb.add_field(name="Message Content:", value=f"{message.content}")
