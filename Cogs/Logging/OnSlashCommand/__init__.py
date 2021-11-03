from .on_slash_command import Logging


def setup(bot):
    bot.add_cog(Logging(bot))
