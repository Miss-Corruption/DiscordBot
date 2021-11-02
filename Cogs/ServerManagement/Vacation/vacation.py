from disnake.ext.commands import Cog, Bot

from Data.Database.author import Authors


class VacationTimer:
    __slots__ = ("author", "wp_name", "went_away_on", "vac_days")

    def __init__(self, *, record: Authors):
        self.id = record.id

        self.author = record.author_id
        self.wp_name = record.wp_name
        self.went_away_on = record.went_away_on
        self.vac_days = record.vac_days

    @classmethod
    def temporary(cls, *, author, wp_name, went_away_on, vac_days):
        pseudo = {
            "author": author,
            "wp_name": wp_name,
            "went_away_on": went_away_on,
            "vac_days": vac_days,
        }
        return cls(record=Authors(**pseudo))

    def __eq__(self, other):
        try:
            return self.id == other.id
        except AttributeError:
            return False

    def __hash__(self):
        return hash(self.id)


class VacationCommand(Cog, name="Services.Vacation"):
    def __init__(self, bot: Bot):
        self.bot = bot
