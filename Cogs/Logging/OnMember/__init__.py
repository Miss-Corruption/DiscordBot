from .on_member import Logging


def setup(bot):
    bot.add_cog(Logging(bot))
