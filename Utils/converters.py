import dateparser
import disnake
from disnake.ext import commands


class Time:
    settings = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": True,
        "TIMEZONE": "Europe/Berlin",
    }

    def __init__(self, inter: disnake.ApplicationCommandInteraction, argument: str):
        now = inter.created_at
        self.argument = argument

        dt = dateparser.parse(argument, settings=self.settings)

        if dt is None:
            raise commands.BadArgument(
                'Invalid time provided, try e.g. "tomorrow" or "3 days"'
            )

        for field in ("hour", "minute", "second", "microsecond"):
            if getattr(dt, field) is None:
                setattr(dt, field, getattr(now, field))

        self.dt = dt
        self._past = dt < now


class FutureTime(Time):
    def __init__(self, inter: disnake.ApplicationCommandInteraction, argument: str):
        super().__init__(inter, argument)

        if self._past:
            raise commands.BadArgument("This time is in the past")


async def futuretime_autocomp(inter, value):
    try:
        converted = FutureTime(inter, value)
    except commands.BadArgument as exc:
        return {str(exc): value}
    return {converted.dt.strftime("on %a, %d %b %Y, at %H:%M:%S in UTC"): value}
