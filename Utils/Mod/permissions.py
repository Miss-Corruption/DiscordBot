import logging
import disnake
import traceback
from disnake.ext import commands
from disnake.ext.commands.base_core import InvokableApplicationCommand
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from Utils.Configuration import config


logger = logging.getLogger(__name__)


class CustomBot(commands.Bot):
    async def _sync_application_commands(self) -> None:
        try:
            # register commands
            await super()._sync_application_commands()
            if not self._sync_commands:
                return

            guild_id = config.GUILD_ID[0]

            # TODO: workaround until this is fixed: https://github.com/EQUENOS/disnake/blob/95c1cd4ff2cdf62232ffcba6422e91a6b11a14bb/disnake/state.py#L1590
            if isinstance(self._connection._guild_application_commands.get(guild_id), set):
                await self._cache_application_commands()

            # collect new permissions
            new_permissions: Dict[str, disnake.PartialGuildAppCmdPerms] = {}

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
                assert command.name not in new_permissions
                new_permissions[command.name] = await reqs.to_perms(self, guild_command.id)

            if new_permissions:
                perms_list = "\n".join(
                    f'\t{n}: {[p.to_dict() for p in v.permissions]}'
                    for n, v in new_permissions.items()
                )
                logger.debug(f'setting new permissions:\n{perms_list}')

                await self.bulk_edit_command_permissions(guild_id, list(new_permissions.values()))
                logger.debug('successfully set permissions')

        except Exception as e:
            print('unable to update slash commands or permissions:')
            traceback.format_exc()
            exit(1)  # can't re-raise, since we're running in a separate task without error handling


def allow(
    *,
    role_ids: Optional[Dict[int, bool]] = None,
    user_ids: Optional[Dict[int, bool]] = None,
    owner: Optional[bool] = None
) -> Callable[[InvokableApplicationCommand], InvokableApplicationCommand]:
    def wrap(cmd: InvokableApplicationCommand) -> InvokableApplicationCommand:
        if isinstance(cmd, InvokableApplicationCommand):
            app_cmd = cmd
        else:
            assert False, f'permissions cannot be set on `{type(cmd).__name__}` objects'

        assert app_cmd.body.default_permission is False, \
            f'custom command permissions require `default_permission = False` (command: \'{app_cmd.qualified_name}\')'
        setattr(app_cmd, '__app_cmd_perms__', _AppCommandPermissions(
            role_ids=role_ids,
            user_ids=user_ids,
            owner=owner
        ))
        return cmd
    return wrap


@dataclass(frozen=True)
class _AppCommandPermissions:
    role_ids: Optional[Dict[int, bool]]
    user_ids: Optional[Dict[int, bool]]
    owner: Optional[bool]

    def __post_init__(self) -> None:
        if (not self.role_ids) and (not self.user_ids) and self.owner is None:
            raise disnake.errors.InvalidArgument('at least one of \'role_ids\', \'user_ids\', \'owner\' must be set')

    async def to_perms(self, bot: commands.Bot, command_id: int) -> disnake.PartialGuildAppCmdPerms:
        user_ids = dict(self.user_ids or {})
        # add owner to user IDs
        if self.owner is not None:
            user_ids[int(config.OWNER_ID)] = self.owner

        return disnake.PartialGuildAppCmdPerms(
            command_id,
            role_ids=self.role_ids or {},
            user_ids=user_ids
        )
