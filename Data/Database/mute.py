from . import *


class Mutes(Model):
    id = BigIntField(pk=True)

    expires = DatetimeField()
    created = DatetimeField(auto_now_add=True)
    event = CharField(32)
    author_id = BigIntField()

    class Meta:
        table = "mute"
