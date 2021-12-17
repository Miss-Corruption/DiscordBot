import os
from itertools import chain
from os import listdir, path

from dotenv import load_dotenv

from Rocchan.bot import Rocchan

load_dotenv()

bot = Rocchan("R.")

dirs = chain.from_iterable(
    [
        [
            f"{f}.{_f.replace('.py', '')}"
            if path.isfile(path.join("../Cogs", f, _f))
            else f"{f}.{_f}"
            for _f in listdir(path.join("../Cogs", f))
            if _f not in "__pycache__"
        ]
        for f in listdir("../Cogs")
        if path.isdir(path.join("../Cogs", f)) and f not in ("__init__", "__pycache__")
    ]
)
bot._extensions = [f for f in dirs]
bot.load_extensions()

bot.run(os.environ["BOT_TOKEN"])
