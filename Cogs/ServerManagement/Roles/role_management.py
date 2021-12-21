import json
from typing import Tuple

from disnake import (
    ApplicationCommandInteraction,
    ButtonStyle,
    CategoryChannel,
    Colour,
    Embed,
    Emoji,
    Enum,
    GuildCommandInteraction,
    InteractionResponded,
    InteractionTimedOut,
    Member,
    Message,
    MessageInteraction,
    NotFound,
    PermissionOverwrite,
    Role,
    TextChannel,
)
from disnake.ext.commands import (
    check,
    Cog,
    slash_command,
)
from disnake.ui import Button, View

DEFAULT_EVENT_DESCRIPTION = "This will update itself during on-going Events such as the CrocApoca!! Q&A in the past. Right now there are no reactions as there is no event going on."  # used only during the file creation


class RoleEnum(Enum):  # TODO change the enum values
    Circle = "899546050942095400"
    Brand = "899546150103814144"
    Partner = "899546187105992764"


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


class RoleManagement(Cog, name="ServerManagement.RoleManagement"):
    def __init__(self, bot):
        self.bot = bot

        # TODO change these
        self.file_path = "../Data/Channels.json"
        self.languages_embed = Embed(title="Rules & Roles", color=0x3B1261)

        self.languages_embed.add_field(
            name="Rules",
            value="The English ruleset for the server can be found [here](http://rules.visual-novel.info/en.pdf). "
            "Please read it before assigning yourself a role. \n\n"
            "Das deutsche Regelwerk findet ihr [hier](http://rules.visual-novel.info/de.pdf). "
            "Bitte lest es, bevor ihr euch eine Rolle zuweist.\n\n"
            "このサーバの日本語のルールは[ここ](http://rules.visual-novel.info/jp.pdf)に書いてあります。"
            "ここを読んだら、自分のロールを割り当ててください。",
            inline=False,
        )

        self.languages_embed.add_field(
            name="Language Roles",
            value="React to give yourself the role. Will give you access to all language specific channels. "
            "Not having the role will hide them from you.\n\n"
            "Klicke auf die Emotes um Zugang zu den entsprechenden Sprachen zu erhalten. Ohne entsprechende "
            "Rolle werden dir diese Kanäle nicht angezeigt.\n\n"
            "この投稿の下の国旗の絵文字をクリックすると、各言語別の役職（role）が付与されて、該当する言語のチャンネルにアクセスできるようになります。"
            "役職に設定されていない言語のチャンネルは一覧に表示されません。",
            inline=False,
        )

        self.flavors_embed = Embed(
            title="Flavor Roles",
            description="React for a flavour-role. They aren't needed for any channels. They tell others what your "
            "preferences are. From left to right the flavors are: "
            "Yaoi, Yuri, Loli, Eroge, Otome, SciAdv, All-Ages, Romance, Shounen-Ai\n\n"
            "Klickt auf die Emotes um eine Rolle zu bekommen. Dadurch bekommt ihr Rollen, die eure "
            "Interessen kundgeben, jedoch nicht für bestimmte Channels benötigt werden. Von Links nach "
            "Rechts gibts es die Flavorrollen: Yaoi, Yuri, Loli, Eroge, Otome, SciAdv, All-Ages, Romance, "
            "Shounen-Ai\n\n"
            "この投稿の下の絵文字をクリックして、あなたの趣向を役職に設定してください。役職がなくてもチャンネルへのアクセスはできますが、他のメンバーがあなたの好みを把握することができます。左から順に"
            "Yaoi(成人向けBL)、yuri(百合)、loli(ロリ)、eroge(エロゲ)、otome(乙女ゲ)、SciAdv(科学アドベンチャー)、"
            "All-Ages(全年齢向け)、Romance(純愛系)、Shounen-Ai(≒全年齢向けBL)",
            color=0x3B1261,
        )

        self.event_embed = Embed(
            title="Event Roles",
            color=0x3B1261,
        )

        # Opening JSON file
        try:
            with open(self.file_path, "r") as json_file:
                try:
                    self.data = json.load(json_file)
                except json.JSONDecodeError:
                    self.data = {}
        except FileNotFoundError:
            with open(self.file_path, "w"):
                self.data = {}

        if "Languages" not in self.data:
            self.data["Languages"] = {}

        if "Flavors" not in self.data:
            self.data["Flavors"] = {}

        self.event_embed.description = DEFAULT_EVENT_DESCRIPTION

        if "Event" not in self.data:
            self.data["Event"] = {"default_description": DEFAULT_EVENT_DESCRIPTION}
        elif "description" in self.data["Event"] and self.data["Event"]["description"]:
            self.event_embed.description = self.data["Event"]["description"]

    """ METHODS """

    async def save_data(self, *args) -> None:
        with open("../Data/Channels.json", "w") as json_file:
            json.dump(
                self.data, json_file, indent=2
            )  # this commit the changes to the json file

        await self.update_messages()

    def generate_views(self) -> Tuple[View, View, View]:
        view_lang = View(timeout=None)
        view_flavor = View(timeout=None)
        view_event = View(timeout=None)

        for lang in self.data["Languages"]:
            view_lang.add_item(
                Button(
                    style=ButtonStyle.primary,
                    custom_id=lang,
                    label=lang,
                    emoji=self.data["Languages"][lang]["emoji"],
                )
            )

        view_flavor.add_item(
            Button(
                style=ButtonStyle.primary,
                custom_id="NSFW",
                label="NSFW",
                emoji=self.data["Selection"]["NSFW_role"]["emoji"],
            )
        )

        for flavor in self.data["Flavors"]:
            view_flavor.add_item(
                Button(
                    style=ButtonStyle.primary,
                    custom_id=flavor,
                    label=flavor,
                    emoji=self.data["Flavors"][flavor]["emoji"],
                )
            )

        if "role_id" in self.data["Event"] and self.data["Event"]["role_id"]:
            view_event.add_item(
                Button(
                    style=ButtonStyle.primary,
                    custom_id="event",
                    label=self.data["Event"]["name"],
                    emoji=self.data["Event"]["emoji"],
                )
            )

        return view_lang, view_flavor, view_event

    async def update_messages(self) -> bool:
        if (
            "Selection" in self.data
            and "channel_id" in self.data["Selection"]
            and self.data["Selection"]["channel_id"]
            and "Languages_message_id" in self.data["Selection"]
            and self.data["Selection"]["Languages_message_id"]
            and "Flavors_message_id" in self.data["Selection"]
            and self.data["Selection"]["Flavors_message_id"]
            and "message_id" in self.data["Event"]
            and self.data["Event"]["message_id"]
        ):
            view_lang, view_flavor, view_event = self.generate_views()

            try:
                channel: TextChannel = self.bot.get_channel(
                    int(self.data["Selection"]["channel_id"])
                ) or await self.bot.fetch_channel(
                    int(self.data["Selection"]["channel_id"])
                )
                msg_lang: Message = await channel.fetch_message(
                    int(self.data["Selection"]["Languages_message_id"])
                )
                msg_flavor: Message = await channel.fetch_message(
                    int(self.data["Selection"]["Flavors_message_id"])
                )

                if [a["components"] for a in view_lang.to_components()] != [
                    [
                        {
                            "type": int(b.type),
                            "style": int(b.style),
                            "label": b.label,
                            "disabled": b.disabled,
                            "custom_id": b.custom_id,
                        }
                        for b in a.children
                    ]
                    for a in msg_lang.components
                ]:
                    await msg_lang.edit(
                        embed=self.languages_embed or None,
                        view=view_lang,
                    )

                if [a["components"] for a in view_flavor.to_components()] != [
                    [
                        {
                            "type": int(b.type),
                            "style": int(b.style),
                            "label": b.label,
                            "disabled": b.disabled,
                            "custom_id": b.custom_id,
                        }
                        for b in a.children
                    ]
                    for a in msg_flavor.components
                ]:
                    await msg_flavor.edit(
                        embed=self.flavors_embed or None,
                        view=view_flavor,
                    )

                if "message_id" in self.data["Event"]:
                    msg_event: Message = await channel.fetch_message(
                        int(self.data["Event"]["message_id"])
                    )

                    if [a["components"] for a in view_event.to_components()] != [
                        [
                            {
                                "type": int(b.type),
                                "style": int(b.style),
                                "label": b.label,
                                "disabled": b.disabled,
                                "custom_id": b.custom_id,
                            }
                            for b in a.children
                        ]
                        for a in msg_event.components
                    ]:
                        if self.data["Event"]["role_id"]:
                            await msg_event.edit(
                                embed=self.event_embed or None,
                                view=view_event,
                            )
                        else:
                            await msg_event.edit(
                                embed=self.event_embed or None,
                                view=view_event,
                            )

                return True
            except NotFound:
                pass

        return False

    """ EVENTS """

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if before.roles == after.roles:
            return

        added = False

        if len(before.roles) > len(after.roles):
            roles = set(before.roles) - set(after.roles)
        else:
            added = True
            roles = set(after.roles) - set(before.roles)

        lang_roles = set([l["role_id"] for l in self.data["Languages"].values()])
        flavor_roles = set([f["role_id"] for f in self.data["Flavors"].values()])
        roles_id = set([r.id for r in roles])

        if not roles_id & lang_roles | flavor_roles:
            return

        roles_id_history = set([r.id for r in before.roles]) | set(
            [r.id for r in after.roles]
        )
        member_lang_roles = None

        if roles_id_history & lang_roles:
            member_lang_roles = {
                after.guild.get_role(int(r)) for r in roles_id_history & lang_roles
            }

        if (
            "Selection" in self.data
            and "NSFW_role" in self.data["Selection"]
            and self.data["Selection"]["NSFW_role"]["id"] in roles_id
        ):
            if added:
                for flavor in self.data["Flavors"]:
                    if (
                        self.data["Flavors"][flavor]["NSFW"]
                        and after.id in self.data["Flavors"][flavor]["members"]
                        and after.id not in self.data["Flavors"][flavor]["blacklist"]
                    ):
                        if member_lang_roles:
                            for member_lang_role in member_lang_roles:
                                channel: TextChannel = after.guild.get_channel(
                                    int(
                                        self.data["Languages"][member_lang_role.name][
                                            "flavor_channels"
                                        ][flavor]
                                    )
                                ) or await after.guild.fetch_channel(
                                    int(
                                        self.data["Languages"][member_lang_role.name][
                                            "flavor_channels"
                                        ][flavor]
                                    )
                                )
                                overwrites = channel.overwrites

                                if after in overwrites:
                                    overwrites[after].view_channel = True
                                else:
                                    overwrites[after] = PermissionOverwrite(
                                        **{"view_channel": True}
                                    )

                                await channel.edit(overwrites=overwrites)

                        if after.id not in self.data["Flavors"][flavor]["members"]:
                            self.data["Flavors"][flavor]["members"].append(after.id)
            else:
                for flavor in self.data["Flavors"]:
                    if (
                        self.data["Flavors"][flavor]["NSFW"]
                        and after.id in self.data["Flavors"][flavor]["members"]
                    ):
                        if member_lang_roles:
                            for member_lang_role in member_lang_roles:
                                channel: TextChannel = after.guild.get_channel(
                                    int(
                                        self.data["Languages"][member_lang_role.name][
                                            "flavor_channels"
                                        ][flavor]
                                    )
                                ) or await after.guild.fetch_channel(
                                    int(
                                        self.data["Languages"][member_lang_role.name][
                                            "flavor_channels"
                                        ][flavor]
                                    )
                                )
                                overwrites = channel.overwrites

                                if after in overwrites:
                                    del overwrites[after]
                                    await channel.edit(overwrites=overwrites)

        if roles_id & flavor_roles:
            for role in roles:
                if added and after.id in self.data["Flavors"][role.name]["blacklist"]:
                    continue

                if member_lang_roles:
                    for member_lang_role in member_lang_roles:
                        channel: TextChannel = after.guild.get_channel(
                            int(
                                self.data["Languages"][member_lang_role.name][
                                    "flavor_channels"
                                ][role.name]
                            )
                        ) or await after.guild.fetch_channel(
                            int(
                                self.data["Languages"][member_lang_role.name][
                                    "flavor_channels"
                                ][role.name]
                            )
                        )
                        overwrites = channel.overwrites

                        if channel.nsfw:
                            nsfw_role = after.guild.get_role(
                                int(self.data["Selection"]["NSFW_role"]["id"])
                            )

                            if nsfw_role not in after.roles:
                                continue

                        if not added:
                            del overwrites[after]
                            await channel.edit(overwrites=overwrites)
                        else:
                            if after in overwrites:
                                overwrites[after].view_channel = True
                            else:
                                overwrites[after] = PermissionOverwrite(
                                    **{"view_channel": True}
                                )

                            await channel.edit(overwrites=overwrites)

                if not added:
                    del self.data["Flavors"][role.name]["members"][
                        self.data["Flavors"][role.name]["members"].index(after.id)
                    ]
                else:
                    if "members" not in self.data["Flavors"][role.name]:
                        self.data["Flavors"][role.name]["members"] = []

                    self.data["Flavors"][role.name]["members"].append(after.id)

        if roles_id & lang_roles:
            if not added:
                for flavor in self.data["Flavors"]:
                    if (
                        "members" not in self.data["Flavors"][flavor]
                        or after.id not in self.data["Flavors"][flavor]["members"]
                    ):
                        continue

                    for lang_role in {
                        after.guild.get_role(int(r)) for r in roles_id & lang_roles
                    }:
                        channel: TextChannel = after.guild.get_channel(
                            int(
                                self.data["Languages"][lang_role.name][
                                    "flavor_channels"
                                ][flavor]
                            )
                        ) or await after.guild.fetch_channel(
                            int(
                                self.data["Languages"][lang_role.name][
                                    "flavor_channels"
                                ][flavor]
                            )
                        )
                        overwrites = channel.overwrites

                        if after in overwrites:
                            del overwrites[after]
                            await channel.edit(overwrites=overwrites)
            else:
                for flavor in self.data["Flavors"]:
                    if (
                        "members" not in self.data["Flavors"][flavor]
                        or after.id not in self.data["Flavors"][flavor]["members"]
                    ):
                        continue

                    for lang_role in {
                        after.guild.get_role(int(r)) for r in roles_id & lang_roles
                    }:
                        channel: TextChannel = after.guild.get_channel(
                            int(
                                self.data["Languages"][lang_role.name][
                                    "flavor_channels"
                                ][flavor]
                            )
                        ) or await after.guild.fetch_channel(
                            int(
                                self.data["Languages"][lang_role.name][
                                    "flavor_channels"
                                ][flavor]
                            )
                        )
                        overwrites = channel.overwrites

                        if after in overwrites:
                            overwrites[after].view_channel = True
                        else:
                            overwrites[after] = PermissionOverwrite(
                                **{"view_channel": True}
                            )

                        await channel.edit(overwrites=overwrites)

        await self.save_data()

    @Cog.listener()
    async def on_slash_command_completion(self, _inter: ApplicationCommandInteraction):
        await self.save_data()

    # @Cog.listener()
    # async def on_button_click(self, inter: MessageInteraction):
    #     if (
    #         "Selection" not in self.data
    #         or self.data["Selection"]["channel_id"] != inter.channel.id
    #     ):
    #         return
    #
    #     if inter.message.id == self.data["Selection"]["Languages_message_id"]:
    #         lang_roles = set([l["role_id"] for l in self.data["Languages"].values()])
    #         author_roles = set([r.id for r in inter.author.roles])
    #         resp = ""
    #
    #         if (
    #             self.data["Languages"][inter.component.custom_id]["role_id"]
    #             not in author_roles
    #         ):
    #             await inter.author.add_roles(
    #                 inter.guild.get_role(
    #                     int(
    #                         self.data["Languages"][inter.component.custom_id]["role_id"]
    #                     )
    #                 )
    #             )
    #
    #             resp += (
    #                 ("\n" if resp else "")
    #                 + f"The language `@{inter.component.custom_id}` has been added successfully"
    #             )
    #         else:
    #             await inter.author.remove_roles(
    #                 inter.guild.get_role(
    #                     int(
    #                         self.data["Languages"][inter.component.custom_id]["role_id"]
    #                     )
    #                 )
    #             )
    #             role = inter.guild.get_role(int(list(author_roles & lang_roles)[0]))
    #
    #             resp = f"The language `@{role.name}` has been removed successfully"
    #
    #         try:
    #             await inter.response.send_message(content=resp, ephemeral=True)
    #         except (InteractionTimedOut, InteractionResponded):
    #             return await inter.followup.send(
    #                 resp,
    #                 ephemeral=True,
    #             )
    #     elif inter.message.id == self.data["Selection"]["Flavors_message_id"]:
    #         lang_roles = set([l["role_id"] for l in self.data["Languages"].values()])
    #         author_roles = set([r.id for r in inter.author.roles])
    #
    #         if not author_roles & set(lang_roles):
    #             try:
    #                 return await inter.response.send_message(
    #                     "You must choose a language before choosing a flavor!",
    #                     ephemeral=True,
    #                 )
    #             except (InteractionTimedOut, InteractionResponded):
    #                 return await inter.followup.send(
    #                     "You must choose a language before choosing a flavor!",
    #                     ephemeral=True,
    #                 )
    #         elif inter.component.custom_id == "NSFW":
    #             nsfw_role = inter.guild.get_role(
    #                 int(self.data["Selection"]["NSFW_role"]["id"])
    #             )
    #
    #             if nsfw_role not in inter.author.roles:
    #                 await inter.author.add_roles(nsfw_role)
    #
    #                 try:
    #                     return await inter.response.send_message(
    #                         "The NSFW role has been added successfully!",
    #                         ephemeral=True,
    #                     )
    #                 except (InteractionTimedOut, InteractionResponded):
    #                     return await inter.followup.send(
    #                         "The NSFW role has been added successfully!",
    #                         ephemeral=True,
    #                     )
    #             else:
    #                 await inter.author.remove_roles(nsfw_role)
    #
    #                 try:
    #                     return await inter.response.send_message(
    #                         "The NSFW role has been removed successfully (therefore all the NSFW flavors you were subscribed to were removed)!",
    #                         ephemeral=True,
    #                     )
    #                 except (InteractionTimedOut, InteractionResponded):
    #                     return await inter.followup.send(
    #                         "The NSFW role has been removed successfully (therefore all the NSFW flavors you were subscribed to were removed)!",
    #                         ephemeral=True,
    #                     )
    #         elif (
    #             inter.author.id
    #             in self.data["Flavors"][inter.component.custom_id]["blacklist"]
    #         ):
    #             try:
    #                 return await inter.response.send_message(
    #                     "You choose this flavor because you're blacklisted from it!",
    #                     ephemeral=True,
    #                 )
    #             except (InteractionTimedOut, InteractionResponded):
    #                 return await inter.followup.send(
    #                     "You choose this flavor because you're blacklisted from it!",
    #                     ephemeral=True,
    #                 )
    #         elif self.data["Flavors"][inter.component.custom_id]["NSFW"]:
    #             nsfw_role = inter.guild.get_role(
    #                 int(self.data["Selection"]["NSFW_role"]["id"])
    #             )
    #
    #             if nsfw_role not in inter.author.roles:
    #                 try:
    #                     return await inter.response.send_message(
    #                         "You must have the NSFW role before choosing an NSFW flavor!",
    #                         ephemeral=True,
    #                     )
    #                 except (InteractionTimedOut, InteractionResponded):
    #                     return await inter.followup.send(
    #                         "You must have the NSFW role before choosing an NSFW flavor!",
    #                         ephemeral=True,
    #                     )
    #
    #         if (
    #             "members" in self.data["Flavors"][inter.component.custom_id]
    #             and inter.author.id
    #             in self.data["Flavors"][inter.component.custom_id]["members"]
    #         ):
    #             await inter.author.remove_roles(
    #                 inter.guild.get_role(
    #                     int(self.data["Flavors"][inter.component.custom_id]["role_id"])
    #                 )
    #             )
    #             resp = f"The flavor `@{inter.component.custom_id}` has been removed successfully"
    #         else:
    #             await inter.author.add_roles(
    #                 inter.guild.get_role(
    #                     int(self.data["Flavors"][inter.component.custom_id]["role_id"])
    #                 )
    #             )
    #             resp = f"The flavor `@{inter.component.custom_id}` has been added successfully"
    #
    #         try:
    #             await inter.response.send_message(content=resp, ephemeral=True)
    #         except (InteractionTimedOut, InteractionResponded):
    #             return await inter.followup.send(
    #                 resp,
    #                 ephemeral=True,
    #             )
    #     elif (
    #         "message_id" in self.data["Event"]
    #         and inter.message.id == self.data["Event"]["message_id"]
    #     ):
    #         role = inter.guild.get_role(int(self.data["Event"]["role_id"]))
    #
    #         if role in inter.author.roles:
    #             await inter.author.remove_roles(role)
    #             resp = f"The event role `@{role}` has been removed successfully"
    #         else:
    #             await inter.author.add_roles(role)
    #             resp = f"The event role `@{role}` has been added successfully"
    #
    #         try:
    #             await inter.response.send_message(content=resp, ephemeral=True)
    #         except (InteractionTimedOut, InteractionResponded):
    #             return await inter.followup.send(
    #                 resp,
    #                 ephemeral=True,
    #             )
    #
    #         await self.save_data()

    """ SLASH COMMANDS GROUPS """

    @slash_command(
        name="language",
        description="Manage the languages",
    )
    @is_dev()
    async def language(self, inter: GuildCommandInteraction):
        pass

    @slash_command(
        name="flavor",
        description="Manage the flavors",
    )
    @is_dev()
    async def flavor(self, inter: GuildCommandInteraction):
        pass

    @slash_command(
        name="role",
        description="Manage the roles",
    )
    @is_dev()
    async def role(self, inter: GuildCommandInteraction):
        pass

    @slash_command(
        name="event",
        description="Manage the event",
    )
    @is_dev()
    async def event(self, inter: GuildCommandInteraction):
        pass

    """ SLASH COMMANDS """

    """ LANGUAGES """

    @language.sub_command(
        name="create",
        description="creates a new language and everything that goes with and add it to the json file",
    )
    async def create_language(
        self,
        inter: GuildCommandInteraction,
        name: str,
        emoji: Emoji,
        colour: Colour = Colour.random(),
    ):
        await inter.response.defer(ephemeral=True)

        role = await inter.guild.create_role(name=name, colour=colour)

        overwrites = {
            role: PermissionOverwrite(
                **{"view_channel": True, "read_messages": True, "send_messages": True}
            ),
            inter.guild.default_role: PermissionOverwrite(**{"view_channel": False}),
        }

        ctg = await inter.guild.create_category(name=f"{name}", overwrites=overwrites)
        self.data["Languages"][name] = {
            "id": ctg.id,
            "emoji": emoji,
            "role_id": role.id,
            "colour": colour.to_rgb(),
            "flavor_channels": {},
        }

        for flavor in self.data["Flavors"]:
            channel = await ctg.create_text_channel(name=f"{flavor}")
            self.data["Languages"][name]["flavor_channels"][flavor] = channel.id
            self.data["Flavors"][flavor]["channels_id"].append(channel.id)

        await inter.edit_original_message(
            content=f"Language `{name}` created successfully!",
        )

    @language.sub_command(
        name="edit",
        description="edit an existing language and everything that goes with and modify it in the json file",
    )
    async def edit_language(
        self,
        inter: GuildCommandInteraction,
        name: str,
        new_name: str = None,
        emoji: Emoji = None,
        colour: Colour = None,
    ):
        if name not in self.data["Languages"]:
            return await inter.response.send_message(
                f"This language doesn't exist! `{name}`", ephemeral=True
            )
        elif not new_name and not emoji and not colour:
            return await inter.response.send_message(
                f"Please choose at least one option to edit!", ephemeral=True
            )
        elif not new_name:
            new_name = name

        await inter.response.defer(ephemeral=True)

        self.data["Languages"][new_name] = {
            "emoji": emoji if emoji else self.data["Languages"][name]["emoji"],
            "id": self.data["Languages"][name]["id"],
            "role_id": self.data["Languages"][name]["role_id"],
            "colour": colour.to_rgb()
            if colour
            else (*self.data["Languages"][name]["colour"],),
            "flavor_channels": self.data["Languages"][name]["flavor_channels"],
        }

        if new_name != name:
            del self.data["Languages"][name]

        ctg = inter.guild.get_channel(
            int(self.data["Languages"][new_name]["id"])
        ) or await inter.guild.fetch_channel(
            int(self.data["Languages"][new_name]["id"])
        )
        role = inter.guild.get_role(int(self.data["Languages"][new_name]["role_id"]))
        await ctg.edit(name=f"{emoji} {new_name}")
        await role.edit(
            name=new_name,
            colour=colour
            if colour
            else Colour.from_rgb(*self.data["Languages"][new_name]["colour"]),
        )

        await inter.edit_original_message(
            content=f"Language `{name}` {f'(now `{new_name}`)' if new_name != name else ''} edited successfully!",
        )

    @language.sub_command(
        name="delete",
        description="delete an existing language and everything that goes with and modify it in the json file",
    )
    async def delete_language(
        self,
        inter: GuildCommandInteraction,
        name: str,
    ):
        if name not in self.data["Languages"]:
            return await inter.response.send_message(
                f"This language doesn't exist! `{name}`", ephemeral=True
            )

        await inter.response.defer(ephemeral=True)

        for flavor_channel in self.data["Languages"][name]["flavor_channels"]:
            channel = inter.guild.get_channel(
                int(self.data["Languages"][name]["flavor_channels"][flavor_channel])
            ) or await inter.guild.fetch_channel(
                int(self.data["Languages"][name]["flavor_channels"][flavor_channel])
            )
            await channel.delete()
            del self.data["Flavors"][flavor_channel]["channels_id"][
                self.data["Flavors"][flavor_channel]["channels_id"].index(channel.id)
            ]

        ctg = inter.guild.get_channel(
            int(self.data["Languages"][name]["id"])
        ) or await inter.guild.fetch_channel(int(self.data["Languages"][name]["id"]))
        await ctg.delete()
        role = inter.guild.get_role(int(self.data["Languages"][name]["role_id"]))
        await role.delete()
        del self.data["Languages"][name]
        await inter.edit_original_message(
            content=f"Language `{name}` deleted successfully!",
        )

    """ FLAVORS """

    @flavor.sub_command(
        name="create",
        description="creates a new flavor and everything that goes with and add it to the json file",
    )
    async def create_flavor(
        self,
        inter: GuildCommandInteraction,
        name: str,
        emoji: Emoji,
        nsfw: bool = False,
    ):
        await inter.response.defer(ephemeral=True)

        role = await inter.guild.create_role(name=name)
        self.data["Flavors"][name] = {
            "NSFW": nsfw,
            "emoji": emoji,
            "role_id": role.id,
            "channels_id": [],
            "members": [],
            "blacklist": [],
        }

        for language in self.data["Languages"]:
            ctg: CategoryChannel = inter.guild.get_channel(
                int(self.data["Languages"][language]["id"])
            ) or await inter.guild.fetch_channel(
                int(self.data["Languages"][language]["id"])
            )
            channel = await ctg.create_text_channel(
                name=f"{name}",
                nsfw=nsfw,
                overwrites={
                    inter.guild.default_role: PermissionOverwrite(
                        **{"view_channel": False}
                    )
                },
            )
            self.data["Flavors"][name]["channels_id"].append(channel.id)
            self.data["Languages"][language]["flavor_channels"][name] = channel.id

        await inter.edit_original_message(
            content=f"Flavor `{name}` created successfully!",
        )

    @flavor.sub_command(
        name="edit",
        description="edit an existing flavor and everything that goes with and modify it in the json file",
    )
    async def edit_flavor(
        self,
        inter: GuildCommandInteraction,
        name: str,
        new_name: str = None,
        emoji: str = None,
        nsfw: bool = None,
    ):
        if name not in self.data["Flavors"]:
            return await inter.response.send_message(
                f"This flavor doesn't exist! `{name}`", ephemeral=True
            )
        elif not new_name and not emoji and nsfw is None:
            return await inter.response.send_message(
                f"Please choose at least one option to edit!", ephemeral=True
            )
        elif not new_name:
            new_name = name

        await inter.response.defer(ephemeral=True)

        self.data["Flavors"][new_name] = {
            "emoji": emoji if emoji else self.data["Flavors"][name]["emoji"],
            "channels_id": self.data["Flavors"][name]["channels_id"],
            "members": self.data["Flavors"][name]["members"],
            "role_id": self.data["Flavors"][name]["role_id"],
            "NSFW": nsfw if nsfw is not None else self.data["Flavors"][name]["NSFW"],
            "blacklist": self.data["Flavors"][name]["blacklist"],
        }

        for language in self.data["Languages"].values():
            del language["flavor_channels"][name]
            language["flavor_channels"][new_name] = self.data["Flavors"][name][
                "channels_id"
            ]

        if new_name != name:
            del self.data["Flavors"][name]

        role = inter.guild.get_role(int(self.data["Flavors"][new_name]["role_id"]))
        await role.edit(
            name=new_name,
        )

        for channel_id in self.data["Flavors"][new_name]["channels_id"]:
            channel: TextChannel = inter.guild.get_channel(
                channel_id
            ) or await inter.guild.fetch_channel(channel_id)

            if nsfw is None:
                await channel.edit(name=f"{new_name}")
            else:
                await channel.edit(
                    name=f"{new_name}",
                    nsfw=nsfw,
                )

        await inter.edit_original_message(
            content=f"Flavor `{name}` {f'(now `{new_name}`)' if new_name != name else ''} edited successfully!",
        )

    @flavor.sub_command(
        name="delete",
        description="delete an existing flavor and everything that goes with and modify it in the json file",
    )
    async def delete_flavor(
        self,
        inter: GuildCommandInteraction,
        name: str,
    ):
        if name not in self.data["Flavors"]:
            return await inter.response.send_message(
                f"This flavor doesn't exist! `{name}`", ephemeral=True
            )

        await inter.response.defer(ephemeral=True)

        for channel in self.data["Flavors"][name]["channels_id"]:
            channel = inter.guild.get_channel(
                int(channel)
            ) or await inter.guild.fetch_channel(int(channel))
            await channel.delete()

        for language in self.data["Languages"].values():
            del language["flavor_channels"][name]

        role = inter.guild.get_role(int(self.data["Flavors"][name]["role_id"]))
        await role.delete()

        del self.data["Flavors"][name]
        await inter.edit_original_message(
            content=f"Flavor `{name}` deleted successfully!",
        )

    @flavor.sub_command(
        name="blacklist_member",
        description="Blacklist a member from a flavor",
    )
    async def blacklist_member_flavor(
        self, inter: GuildCommandInteraction, member: Member, flavor: str
    ):
        if flavor not in self.data["Flavors"]:
            return await inter.response.send_message(
                f"This flavor doesn't exist! `{flavor}`", ephemeral=True
            )
        elif member.id in self.data["Flavors"][flavor]["blacklist"]:
            return await inter.response.send_message(
                f"The member `{member}` is already blacklisted from the flavor `{flavor}`",
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)
        role = inter.guild.get_role(int(self.data["Flavors"][flavor]["role_id"]))
        await member.remove_roles(role)

        self.data["Flavors"][flavor]["blacklist"].append(member.id)
        await inter.edit_original_message(
            content=f"The member `{member}` has been blacklisted from the flavor `{flavor}`"
        )

    @flavor.sub_command(
        name="whitelist_member",
        description="Removes a member from a flavor's blacklist",
    )
    async def whitelist_member_flavor(
        self, inter: GuildCommandInteraction, member: Member, flavor: str
    ):
        if flavor not in self.data["Flavors"]:
            return await inter.response.send_message(
                f"This flavor doesn't exist! `{flavor}`", ephemeral=True
            )
        elif member.id not in self.data["Flavors"][flavor]["blacklist"]:
            return await inter.response.send_message(
                f"The member `{member}` is already not blacklisted from the flavor `{flavor}`",
                ephemeral=True,
            )

        del self.data["Flavors"][flavor]["blacklist"][
            self.data["Flavors"][flavor]["blacklist"].index(member.id)
        ]

        await inter.response.send_message(
            f"The member `{member}` is no longer blacklisted from the flavor `{flavor}`",
            ephemeral=True,
        )

    @flavor.sub_command(
        name="opt_out",
        description="Opt out from the current flavor",
    )
    async def opt_out_flavor(self, inter: GuildCommandInteraction, flavor: str):
        if flavor not in self.data["Flavors"]:
            return await inter.response.send_message(
                f"This flavor doesn't exist! `{flavor}`", ephemeral=True
            )
        elif inter.author.id in self.data["Flavors"][flavor]["blacklist"]:
            return await inter.response.send_message(
                f"You already opted out!",
                ephemeral=True,
            )

        await inter.response.defer(ephemeral=True)
        role = inter.guild.get_role(int(self.data["Flavors"][flavor]["role_id"]))
        await inter.author.remove_roles(role)

        self.data["Flavors"][flavor]["blacklist"].append(inter.author.id)
        await inter.edit_original_message(
            content=f"You successfully opted out from the flavor."
        )

    """ ROLES """

    @role.sub_command(
        name="create",
        description="Creates a new role and sort it according to the type chosen",
    )
    async def create_role(
        self,
        inter: GuildCommandInteraction,
        _type: RoleEnum,
        name: str,
        colour: Colour = Colour.random(),
    ):
        if name in [r.name for r in inter.guild.roles]:
            return await inter.response.send_message(
                "There is already an existing role with this name!",
                ephemeral=True,
            )

        role = await inter.guild.create_role(name=name, colour=colour)
        await role.edit(position=inter.guild.get_role(int(_type)).position)

        await inter.response.send_message(
            content=f"The role `{role}` have been correctly created!", ephemeral=True
        )

    @role.sub_command(
        name="edit",
        description="Edit an existing role and sort it according to the type chosen",
    )
    async def edit_role(
        self,
        inter: GuildCommandInteraction,
        role: Role,
        _type: RoleEnum = None,
        name: str = None,
        colour: Colour = None,
    ):
        if not _type and not name and not colour:
            return await inter.response.send_message(
                f"Please choose at least one option to edit!", ephemeral=True
            )

        edits = {}

        if _type:
            edits["position"] = inter.guild.get_role(int(_type)).position

        if name:
            edits["name"] = name

        if colour:
            edits["colour"] = colour

        await role.edit(**edits)
        await inter.response.send_message(
            content=f"The role `{role}`{f' (now `{name}`)' if name else ''} have been correctly edited!",
            ephemeral=True,
        )

    @role.sub_command(
        name="delete",
        description="Delete an existing role and sort it according to the type chosen",
    )
    async def delete_role(
        self, inter: GuildCommandInteraction, role: Role, reason: str = None
    ):
        await role.delete(reason=reason)
        await inter.response.send_message(
            content=f"The role `{role}` have been correctly deleted!", ephemeral=True
        )

    """ GENERATE SELECTIONS """

    @slash_command(
        name="generate_selections",
        description="creates the selection correctly",
    )
    @is_dev()
    async def generate_selections_slash(self, inter: GuildCommandInteraction):
        if not self.data["Languages"] or not self.data["Flavors"]:
            return await inter.response.send_message(
                "Please have flavors and languages prepared before creating the selection messages",
                ephemeral=True,
            )
        elif "Selection" not in self.data or "NSFW_role" not in self.data["Selection"]:
            return await inter.response.send_message(
                "Please set a NSFW role before creating the selection messages",
                ephemeral=True,
            )
        elif await self.update_messages():
            return await inter.response.send_message(
                "Selections have been correctly updated!", ephemeral=True
            )

        await inter.response.defer(ephemeral=True)

        if "Selection" not in self.data:
            self.data["Selection"] = {}

        view_lang, view_flavor, view_event = self.generate_views()

        msg_lang = await inter.channel.send(
            embed=self.languages_embed or None, view=view_lang
        )
        msg_flavor = await inter.channel.send(
            embed=self.flavors_embed or None, view=view_flavor
        )
        msg_event = await inter.channel.send(
            embed=self.event_embed or None,
            view=view_event,
        )

        self.data["Selection"]["Languages_message_id"] = msg_lang.id
        self.data["Selection"]["Flavors_message_id"] = msg_flavor.id
        self.data["Event"]["message_id"] = msg_event.id
        self.data["Selection"]["channel_id"] = inter.channel.id

        await inter.edit_original_message(
            content="Selections have been correctly created!",
        )

    """ EVENT """

    @event.sub_command(name="set", description="Set a new event")
    async def event_set(
        self, inter: GuildCommandInteraction, description: str, role: Role, emoji: Emoji
    ):
        self.data["Event"]["name"] = role.name
        self.data["Event"]["role_id"] = role.id
        self.data["Event"]["description"] = description
        self.event_embed.description = description
        self.data["Event"]["emoji"] = emoji

        await inter.response.send_message(
            content=f"Event `{role}` successfully set!", ephemeral=True
        )

    @event.sub_command(name="reset", description="Reset the current event")
    async def event_reset(self, inter: GuildCommandInteraction):
        self.data["Event"]["name"] = None
        self.data["Event"]["role_id"] = None
        self.data["Event"]["description"] = None
        self.event_embed.description = self.data["Event"]["default_description"]
        self.data["Event"]["emoji"] = None

        await inter.response.send_message(
            content=f"Event successfully reset!", ephemeral=True
        )

    """ NSFW """

    @slash_command(
        name="set_nsfw",
        description="Set the NSFW role",
    )
    @is_dev()
    async def nsfw_set(
        self, inter: GuildCommandInteraction, role: Role, emoji: Emoji = "🍆"
    ):
        if "Selection" not in self.data:
            self.data["Selection"] = {}

        self.data["Selection"]["NSFW_role"] = {"id": role.id, "emoji": emoji}

        await inter.response.send_message(
            content=f"NSFW role successfully set!", ephemeral=True
        )

    @slash_command(
        name="set_nsfw",
        description="Set the NSFW role",
    )
    @is_dev()
    async def nsfw_set(
        self, inter: GuildCommandInteraction, role: Role, emoji: Emoji = "🍆"
    ):
        if "Selection" not in self.data:
            self.data["Selection"] = {}

        self.data["Selection"]["NSFW_role"] = {"id": role.id, "emoji": emoji}

        await inter.response.send_message(
            content=f"NSFW role successfully set!", ephemeral=True
        )
