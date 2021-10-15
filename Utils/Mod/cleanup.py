import asyncio
from typing import List, Iterable

import disnake


async def mass_purge(messages: List[disnake.Message], channel: disnake.TextChannel):
    while messages:
        try:
            await channel.delete_messages(messages[:100])
        except disnake.errors.HTTPException:
            pass
        messages = messages[100:]
        await asyncio.sleep(1.5)


async def slow_deletion(messages: Iterable[disnake.Message]):
    for message in messages:
        try:
            await message.delete()
        except disnake.HTTPException:
            pass