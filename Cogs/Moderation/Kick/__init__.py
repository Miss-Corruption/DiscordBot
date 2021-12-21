from .Kick import Kick


def setup(bot):
    bot.add_cog(Kick(bot))
