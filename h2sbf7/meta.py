from __future__ import annotations

from typing import TYPE_CHECKING
from nextcord import slash_command, Interaction
from nextcord.ext import commands

if TYPE_CHECKING:
    ...


class BotMeta(commands.Cog, name="Meta"):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Bot-related info.")
    async def meta(self, _: Interaction):
        pass

    @meta.subcommand()
    async def source(self, interaction: Interaction):
        """Show the bot's source code."""

        await interaction.send("https://github.com/maskduck/h2sbf7")


def setup(bot):
    bot.add_cog(BotMeta(bot))
