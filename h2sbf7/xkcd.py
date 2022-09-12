from __future__ import annotations

from typing import TYPE_CHECKING, no_type_check

import requests
from aiohttp import ClientSession, ContentTypeError
from nextcord import (ButtonStyle, Colour, Embed, Interaction, SlashOption,
                      slash_command)
from nextcord.ext import commands
from nextcord.ui import Button, View, button
from orjson import JSONDecodeError as _ORJSON_DECODEERROR
from requests.exceptions import JSONDecodeError
from typing_extensions import Self
from utils import PatchedSlashOption, _decode_with_orjson, rev

if TYPE_CHECKING:
    from ..__main__ import MainBot


class XKCDIterator:
    def __init__(self: Self, count: int):
        self.count = count

    def __next__(self: Self) -> dict:
        self.count += 1
        try:
            r = requests.get(f"https://xkcd.com/{self.count}/info.0.json")
            return r.json()
        except JSONDecodeError:
            self.count = self.count - 1
            return None

    def __rev__(self: Self) -> dict:
        self.count = self.count - 1

        try:
            r = requests.get(f"https://xkcd.com/{self.count}/info.0.json").json()
            return r

        except JSONDecodeError:
            self.count += 1
            return None


class XKCDButton(View):
    def __init__(self: Self, this_xkcd: dict, xkcd_iterator: XKCDIterator):
        self._xkcd_iterator = xkcd_iterator
        self._this_xkcd = this_xkcd
        self._msg_resp = None
        super().__init__()

    @button(label="<")
    async def iterate_to_before_hook(
        self: Self, button: Button, interaction: Interaction
    ):
        await interaction.response.defer()
        raw_xkcd = rev(self._xkcd_iterator)
        if raw_xkcd is None:
            await interaction.send(
                f"It seems like the XKCD comic numbered {self._xkcd_iterator.count - 1} doesn't exist.",
                ephemeral=True,
            )
            return
        embed = Embed(
            title=raw_xkcd["safe_title"],
            url=f"https://xkcd.com/{self._xkcd_iterator.count}",
            description=None,
            color=Colour.green(),
        )
        embed.set_image(url=raw_xkcd["img"])
        embed.set_footer(text=raw_xkcd["alt"])
        self._this_xkcd = raw_xkcd
        await self._msg_resp.edit(embed=embed, view=self)

    @button(label=">")
    async def iterate_to_next_hook(
        self: Self, button: Button, interaction: Interaction
    ) -> None:

        await interaction.response.defer()
        raw_xkcd = next(self._xkcd_iterator)
        if raw_xkcd is None:
            await interaction.send(
                f"It seems like the XKCD comic numbered {self._xkcd_iterator.count + 1} doesn't exist.",
                ephemeral=True,
            )
            return
        embed = Embed(
            title=raw_xkcd["safe_title"],
            url=f"https://xkcd.com/{self._xkcd_iterator.count}",
            description=None,
            color=Colour.green(),
        )
        embed.set_image(url=raw_xkcd["img"])
        embed.set_footer(text=raw_xkcd["alt"])
        self._this_xkcd = raw_xkcd
        await self._msg_resp.edit(embed=embed, view=self)

    @button(label="Get current comic transcript", style=ButtonStyle.green)
    async def get_comic_transcript(
        self: Self, button: Button, interaction: Interaction
    ) -> None:
        await interaction.send(self._this_xkcd["transcript"], ephemeral=True)


class XKCD(commands.Cog):
    def __init__(self: Self, bot: MainBot) -> None:
        self._bot = bot

    @no_type_check
    @slash_command()
    async def xkcd(
        self: Self,
        interaction: Interaction,
        comic_num: int = PatchedSlashOption(
            description="The XKCD number to see. Default to latest.",
            required=False,
            default=requests.get("https://xkcd.com/info.0.json").json()["num"],
        ),
    ) -> None:
        if comic_num:
            async with ClientSession() as session:
                async with session.get(
                    f"https://xkcd.com/{comic_num}/info.0.json"
                ) as r:
                    # print(r)
                    try:
                        raw_xkcd = await _decode_with_orjson(r)
                        # print(r)
                    except (_ORJSON_DECODEERROR):
                        raw_xkcd = None
        else:
            async with ClientSession() as session:
                async with session.get("https://xkcd.com/info.0.json") as r:
                    try:
                        raw_xkcd = await _decode_with_orjson(r)
                        # print(r)
                    except (_ORJSON_DECODEERROR):
                        raw_xkcd = None
        if raw_xkcd is None:
            await interaction.send(
                f"It seems like the XKCD comic numbered {comic_num} doesn't exist.",
                ephemeral=True,
            )
            return
        embed = Embed(
            title=raw_xkcd["safe_title"],
            url=f"https://xkcd.com/{comic_num}",
            description=None,
            color=Colour.green(),
        )
        embed.set_image(url=raw_xkcd["img"])
        embed.set_footer(text=raw_xkcd["alt"])
        view = XKCDButton(raw_xkcd, XKCDIterator(count=comic_num))
        r = await interaction.send(embed=embed, view=view)
        view._msg_resp = r

    @classmethod
    def add_cog_to_bot(cls: XKCD, bot: MainBot):
        bot.add_cog(cls(bot))


setup = XKCD.add_cog_to_bot
