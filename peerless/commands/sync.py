import re
from os import urandom
from typing import Optional

import discord
from discord import app_commands, ui
from discord.ext import commands

from utility import (
    BaseItem,
    BaseView,
    Bot,
    DeferOptions,
    InteractionOptions,
    developer_only,
    get_logger,
    response,
)

logger = get_logger()

class ConfigSelect(BaseItem[ui.Select['ConfigView']], template="^sync:[a-f0-9]{8}$"):
    def __init__(self, item_hex: Optional[str] = None) -> None:
        super().__init__(ui.Select(
            placeholder="Select a config",
            custom_id=f"sync:{item_hex or urandom(4).hex()}",
            options=[
                discord.SelectOption(label="Reload Extensions", value="reload"),
                discord.SelectOption(label="Sync Extensions", value="sync"),
                discord.SelectOption(label="Globally Sync Extensions", value="sync_global"),
                discord.SelectOption(label="Reload Extensions & Sync Commands", value="reload_sync"),
            ],
        ), options=InteractionOptions(
            defer_options=DeferOptions(defer=False, ephemeral=True, thinking=False),
        ))

    @classmethod
    async def from_custom_id(cls, interaction: discord.Interaction, item: ui.Select['ConfigView'], match: re.Match[str], /):
        item_hex = match.group(0).split(':')[1]
        print(f"Creating ConfigSelect from custom_id: {match.group(0)} ({item_hex})", flush=True)
        return cls(item_hex=item_hex)

    async def callback(self, interaction: discord.Interaction['Bot']) -> None:
        guild = self.require_guild(interaction)

        command = self.item.values[0]
        option  = next(x for x in self.item.options if x.value == command)

        option.default = False

        msg = await response.edit(interaction, view=self.view)
        print(getattr(msg, 'id', 'Unknown ID'), flush=True)

        try:
            if command == "reload":
                await interaction.client.load_extensions()

            elif command == "sync":
                interaction.client.tree.copy_global_to(guild=discord.Object(id=guild.id))
                await interaction.client.tree.sync(guild=guild)

            elif command == "sync_global":
                await interaction.client.tree.sync(guild=None)

            else:
                await interaction.client.load_extensions()

                interaction.client.tree.copy_global_to(guild=discord.Object(id=guild.id))
                await interaction.client.tree.sync(guild=guild)
        except Exception as e:
            logger.error(f"Failed to execute `{command}` command", exc_info=e)
            await response.send(interaction, content=f"Failed to execute `{command}` command", ephemeral=True)
            return

        await response.send(interaction, content=f"Successfully executed `{command}` command.", ephemeral=True)

class ConfigView(BaseView):
    def __init__(self) -> None:
        super().__init__()

        self.add_item(ConfigSelect())

class Sync(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @app_commands.command(
        name="sync", 
        description="Sync the bot's commands with Discord", 
        extras={'options': InteractionOptions(
            defer_options=DeferOptions(defer=False, ephemeral=True, thinking=True),
        )}
    )
    @app_commands.guilds(1105641316433547304, 1258570200102469632)
    @developer_only()
    async def sync(self, interaction: discord.Interaction['Bot']) -> None:
        """Sync the bot's commands with Discord."""

        view = ConfigView()
        await response.send(interaction, view=view, ephemeral=True)

async def setup(bot: Bot):
    cog = Sync(bot)
    
    for command in cog.walk_app_commands():
        if hasattr(command, "callback"):
            command.callback.__name__ = f"{cog.qualified_name.lower()}_{command.callback.__name__}" # type: ignore
            command.guild_only = True
    
    await bot.add_cog(cog)