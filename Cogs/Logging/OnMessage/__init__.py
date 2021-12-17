from .on_message import MessageLogging


def setup(bot):
    bot.add_cog(MessageLogging(bot))
