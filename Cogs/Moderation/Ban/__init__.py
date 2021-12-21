from .Ban import Ban


def setup(bot):
    bot.add_cog(Ban(bot))
