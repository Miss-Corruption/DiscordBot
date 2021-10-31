from . import *


class Authors(Model):
    id = BigIntField(pk=True)

    author_id = BigIntField()
    wp_name = CharField(32)
    went_away_on = DatetimeField()
    vac_days = BigIntField()

    class Meta:
        table = "author"
