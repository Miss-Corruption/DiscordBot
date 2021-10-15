import json
import re

from disnake import CategoryChannel, Colour, ApplicationCommandInteraction
from disnake.ext.commands import check, Cog, slash_command, Param, option_enum, Bot

from Utils.Configuration import config


def is_dev():
    async def predicate(ctx):
        return ctx.author.id in [
            149861548876234752,
            210887957723348993,
            226096869724520448,
            481524128818528258,
        ]
        # Deucalion, Tyr, Sinned, Corruption

    return check(predicate)


class RoleManagement(Cog):  # TODO delete name=
    def __init__(self, bot: Bot):
        self.bot = bot
        self.colour_regex = re.compile(r"^#[0-9A-F]{6}$", re.IGNORECASE)
        # Opening JSON file
        with open("data/temp.json", "r") as json_file:
            self.data = json.load(json_file)

    async def save_data(self, *args):
        print("saving...")  # TODO remove this
        with open("data/temp.json", "w") as json_file:
            json.dump(self.data, json_file)  # this commit the changes to the json file

    Mode = option_enum(["Language", "Topic"])

    @slash_command(
        name="create",
        description="Creates a new language and topic depending on selection",
        guild_ids=config.GUILD_ID
    )
    async def create_slash(
            self,
            inter: ApplicationCommandInteraction,
            mode: Mode = Param(
                description="What you want to create"
            ),
            name: str = Param(
                description="The name of your creation"
            ),
            emoji: str = Param(
                description="The emoji you want to use"
            ),
            colour: Colour = Colour.random()):
        match mode:
            case "Language":
                role = await inter.guild.create_role(name=name, colour=colour)
                ctg = await inter.guild.create_category(name=f"{emoji} {name}")
                self.data["Languages"][name] = {
                    "emoji": emoji,
                    "id": ctg.id,
                    "role_id": role.id,
                    "colour": colour.to_rgb()
                }

                for topic in self.data["Topics"]:
                    await ctg.create_text_channel(
                        name=f"{self.data['Topics'][topic]['emoji']} {topic}"
                    )

                await inter.response.send_message(f"Language `{name}` created successfully!")
            case "Topic":
                self.data["Topics"][name] = {"emoji": emoji, "channels_id": []}

                for language in self.data["Languages"].values():
                    ctg: CategoryChannel = inter.guild.get_channel(int(language["id"])) \
                                           or await inter.guild.fetch_channel(int(language["id"]))
                    channel = await ctg.create_text_channel(name=f"{emoji} {name}")
                    self.data["Topics"][name]["channels_id"].append(channel.id)

                await inter.response.send_message(f"Topic `{name}` created successfully!")

    @slash_command(
        name="edit",
        guild_ids=config.GUILD_ID
    )
    async def edit_slash(
            self,
            inter: ApplicationCommandInteraction,
            mode: Mode = Param(
                description="What you want to create"
            ),
            name: str = Param(
                description="The name of your creation"
            ),
            new_name: str = Param(
                description="The name of your creation"
            ),
            emoji: str = Param(
                description="The emoji you want to use"
            ),
            colour: Colour = Colour.random()):
        match mode:
            case "Language":
                if name not in self.data["Languages"]:
                    return await inter.response.reply(f"This language doesn't exist! `{name}`")

                self.data["Languages"][new_name] = {
                    "emoji": emoji,
                    "id": self.data["Languages"][name]["id"],
                    "role_id": self.data["Languages"][name]["role_id"],
                    "colour": colour.to_rgb() if colour else (*self.data["Languages"][name]["colour"],)
                }

                if new_name != name:
                    del self.data["Languages"][name]

                ctg = inter.guild.get_channel(int(self.data["Languages"][name]["id"])) or \
                      await inter.guild.fetch_channel(int(self.data["Languages"][name]["id"]))
                role = inter.guild.get_role(int(self.data["Languages"][new_name]["role_id"]))
                await ctg.edit(name=f"{emoji} {new_name}")
                await role.edit(name=new_name, colour=colour if colour else Colour.from_rgb(
                    *self.data["Languages"][new_name]["colour"]))

                await inter.response.send_message(f"Topic `{name}` created successfully!")(
                    f"Language `{name}` {f'(now `{new_name}`)' if new_name != name else ''} edited successfully!")
            case "Topic":
                if name not in self.data["Topics"]:
                    return await inter.response.reply(f"This topic doesn't exist! `{name}`")

                self.data["Topics"][new_name] = {"emoji": emoji,
                                                 "channels_id": self.data["Topics"][name]["channels_id"]}

                if new_name != name:
                    del self.data["Topics"][name]

                for channel in self.data["Topics"][new_name]["channels_id"]:
                    channel = inter.guild.get_channel(channel) or await inter.guild.fetch_channel(channel)
                    await channel.edit(name=f"{emoji} {new_name}")

                await inter.response.send_message(
                    f"Topic `{name}` {f'(now `{new_name}`)' if new_name != name else ''} edited successfully!")


def setup(bot):
    bot.add_cog(RoleManagement(bot))
