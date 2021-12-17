from tortoise.models import Model
from tortoise.fields import BigIntField, DatetimeField, CharField, JSONField


class Authors(Model):
    id = BigIntField(pk=True)

    author_id = BigIntField()
    wp_name = CharField(32)
    went_away_on = DatetimeField()
    vac_days = BigIntField()

    class Meta:
        table = "author"
