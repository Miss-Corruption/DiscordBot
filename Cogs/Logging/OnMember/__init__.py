from .on_member import MemberLogging


def setup(bot):
    bot.add_cog(MemberLogging(bot))
