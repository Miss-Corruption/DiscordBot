from .report import ReportMessage


def setup(bot):
    bot.add_cog(ReportMessage(bot))
