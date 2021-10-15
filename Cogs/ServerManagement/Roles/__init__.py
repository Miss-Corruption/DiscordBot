from .role_management import RoleManagement


def setup(bot):
    bot.add_cog(RoleManagement(bot))
