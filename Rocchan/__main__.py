import argparse
import os
import traceback
from itertools import chain
from os import listdir, path

from dotenv import load_dotenv
from loguru import logger

from Rocchan.bot import Rocchan

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true")
parser.add_argument("--asyncio-debug", action="store_true")
args = parser.parse_args()

bot = Rocchan("cc!", debug=args.debug, asyncio_debug=args.asyncio_debug)
logger.add(
    "../Logs/Rocchan/{time:YYYY-MM-DD}.log",
    format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
    rotation="500 MB",
    backtrace=True,
    diagnose=True,
    level="TRACE",
)

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
