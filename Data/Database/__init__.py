from tortoise import Tortoise, run_async
from tortoise.expressions import *
from tortoise.transactions import in_transaction

from tortoise.backends.sqlite.client import TransactionWrapper

TORTOISE_ORM = {
    "apps": {
        "author": {
            "models": ["Data.Database.author"],
            "default_connection": "master",
        },
        "remind": {
            "models": ["Data.Database.remind"],
            "default_connection": "master",
        },
    },
    "connections": {"master": "sqlite:..//Data/Database.sqlite"},
}


async def init(*, reload=True):
    if reload:
        await Tortoise.close_connections()
    await Tortoise.init(config=TORTOISE_ORM)
    if reload:
        await Tortoise.generate_schemas()
