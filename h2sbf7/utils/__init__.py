from orjson import loads

from aiohttp import ClientSession


def rev(iter):
    return iter.__rev__()


class EmotionalDamage(Exception):
    ...


def _sendable(embed):
    if len(embed) > 6000:
        raise EmotionalDamage


async def _decode_with_orjson(response):
    try:
        return await response.json(loads=loads, content_type=None)
    except:
        return None


async def _xkcd_latest():
    async with ClientSession() as s:
        async with s.get("https://xkcd.com/info.0.json") as r:
            return _decode_with_orjson(r)


from nextcord import SlashOption


class PatchedSlashOption(SlashOption):
    def verify(self) -> bool:
        return True
