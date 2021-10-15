import logging
import disnake
from disnake.ext import commands
from disnake.ext.commands.base_core import InvokableApplicationCommand
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from Utils.Configuration import config


logger = logging.getLogger(__name__)


class CustomBot(commands.Bot):
    async def _sync_application_commands(self) -> None:
        # register commands
        await super()._sync_application_commands()
        if not self._sync_commands:
            return

        guild_id = config.GUILD_ID

        # TODO: workaround until this is fixed: https://github.com/EQUENOS/disnake/blob/95c1cd4ff2cdf62232ffcba6422e91a6b11a14bb/disnake/state.py#L1590
        if isinstance(self._connection._guild_application_commands.get(guild_id), set):
            await self._cache_application_commands()

        # collect new permissions
        new_permissions: List[disnake.PartialGuildAppCmdPerms] = []

        # iterate over registered command handlers
        for command in self.application_commands:
            # get custom permission data, skip if not set
            reqs: Optional[_AppCommandPermissions] = getattr(command, '__app_cmd_perms__', None)
            if not reqs:
                continue

            # get corresponding guild command (required for guild-specific command ID)
            guild_command = self.get_guild_command_named(guild_id, command.name)
            assert guild_command, f'No guild command with name \'{command.name}\' found in cache, something is broken'
            assert guild_command.id is not None  # this should never fail

            # create new permission data
            new_permissions.append(await reqs.to_perms(self, guild_command.id))

        if new_permissions:
            logger.debug(f'setting new permissions: {new_permissions}')
            await self.bulk_edit_command_permissions(guild_id, new_permissions)


def require(
    *,
    role_ids: Optional[Dict[int, bool]] = None,
    user_ids: Optional[Dict[int, bool]] = None,
    allow_owner: Optional[bool] = None
) -> Callable[[InvokableApplicationCommand], InvokableApplicationCommand]:
    assert any((x is not None) for x in (role_ids, user_ids, allow_owner)), \
        'One of \'role_ids\', \'user_ids\', \'allow_owner\' must not be `None`'

    def wrap(cmd: InvokableApplicationCommand) -> InvokableApplicationCommand:
        setattr(cmd, '__app_cmd_perms__', _AppCommandPermissions(
            role_ids=role_ids,
            user_ids=user_ids,
            allow_owner=allow_owner
        ))
        return cmd
    return wrap


@dataclass(frozen=True)
class _AppCommandPermissions:
    role_ids: Optional[Dict[int, bool]]
    user_ids: Optional[Dict[int, bool]]
    allow_owner: Optional[bool]

    async def to_perms(self, bot: commands.Bot, command_id: int) -> disnake.PartialGuildAppCmdPerms:
        user_ids = dict(self.user_ids or {})
        # add owner to user IDs
        if self.allow_owner is not None:
            user_ids[config.OWNER_ID] = self.allow_owner

        return disnake.PartialGuildAppCmdPerms(
            command_id,
            role_ids=self.role_ids or {},
            user_ids=user_ids
        )
