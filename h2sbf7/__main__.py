from __future__ import annotations

import os

import aiohttp
import uvloop
from dotenv import load_dotenv
from nextcord import Intents
from nextcord.ext import commands

load_dotenv()
import asyncio

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
intents = Intents.all()
intents.typing = False
intents.invites = False
from logging import StreamHandler, getLogger

_log = getLogger("nextcord")
_log.setLevel(1)
_log.addHandler(StreamHandler())


class MainBot(commands.Bot):
    def __init__(self: Self):
        super().__init__(command_prefix=self._get_bot_prefix, intents=intents)
        self.load_extension("xkcd", package="h2sbf7")
        self.load_extension("onami")
        self.load_extension("meta")

    def _get_bot_prefix(self: Self, message, _) -> None:
        # TODO: custom prefixes
        return "-"


bot = MainBot()
bot.run(os.environ["TOKEN"])
