import disnake

from Utils.Configuration import config


async def send_to_action_log(inter: disnake.ApplicationCommandInteraction, embed):
    channel = inter.guild.get_channel(config.ACTION_LOG)
    await channel.send(embed=embed)
