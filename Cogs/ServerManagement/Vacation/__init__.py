from .vacation import VacationCommand


def setup(bot):
    bot.add_cog(VacationCommand(bot))
