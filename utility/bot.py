import asyncio
import importlib
import importlib.util
import traceback
from pathlib import Path
from typing import TYPE_CHECKING, Any, List, Optional, Set, TypeVar

import discord
from discord.app_commands import AppInstallationType, Command, CommandTree
from discord.ext import commands

from .interaction import BaseItem, InteractionOptions, response
from .logger import get_logger
from .namespace import Namespace
from .utils import create_logged_task

if TYPE_CHECKING:
    from .cache import Cache
    from .database import Database

__all__ = (
    'Bot', 
    'Tree',
    'BotT',
)

intents = discord.Intents.none()
intents.guilds  = True
intents.emojis  = True
intents.members = True

member_cache_flags = discord.MemberCacheFlags().none()
member_cache_flags.joined = True

logger = get_logger()

BotT = TypeVar('BotT', None, 'Bot')

class Bot(commands.AutoShardedBot):
    def __init__(self, command_path: str):
        super().__init__(
            tree_cls=Tree,
            command_prefix = [],
            intents = intents,
            member_cache_flags = member_cache_flags,
            max_messages = None,
            chunk_guilds_at_startup = False,
            allowed_installs = AppInstallationType(guild=True, user=False)
        )

        self.command_path = command_path

        self.cache: 'Cache'
        self.database: 'Database'

    async def setup_hook(self) -> None:
        await self.load_extensions()
        assert self.user

        #self.tree.copy_global_to(guild=discord.Object(id=1258570200102469632))
        #await self.tree.sync(guild=discord.Object(id=1258570200102469632))
        
        logger.info(f"Logged in - {self.user.name} ({self.application_id})")
        logger.info(f"Loaded {len([x for x in self.tree.walk_commands() if isinstance(x, Command)])} Commands")

    async def load_extensions(self) -> None:
        self.cog_names: List[str] = []
        path = Path(self.command_path).resolve()

        for file_path in path.rglob('*.py'):
            relative_path = file_path.relative_to(path.parent).with_suffix('')
            cog_path = ".".join(relative_path.parts)

            self.cog_names.append(cog_path)

            try:
                await self.reload_extension(cog_path)
            except commands.ExtensionNotLoaded:
                await self.load_extension(cog_path)

            logger.debug(f"Loaded extension {cog_path!r}")
            self._load_dynamic_item(cog_path)

        return None
    
    def _load_dynamic_item(self, module_path: str) -> None:
        spec = importlib.util.find_spec(module_path)
        if not spec or not spec.loader:
            logger.warning(f"Unable to load module '{module_path}' for dynamic items")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        for obj in module.__dict__.values():
            if not isinstance(obj, type):
                continue

            if (
                issubclass(obj, discord.ui.DynamicItem)
                and obj is not discord.ui.DynamicItem
                and obj is not BaseItem
            ):
                self.add_dynamic_items(obj)
                logger.debug(f"Registered dynamic item {obj.__name__!r} with pattern '{obj.__discord_ui_compiled_template__.pattern}'")

    async def unload_extensions(self) -> None:
        for i in range(0, len(self.cog_names)):
            try:
                await self.unload_extension(self.cog_names[i])
            except commands.ExtensionNotLoaded:
                pass

        return None

class Tree(CommandTree[Bot]):
    async def interaction_check(self, interaction: discord.Interaction[Bot]) -> bool:
        if not self.client.is_ready():
            await interaction.response.send_message(
                content="**The bot is not ready yet. Please try again in a few moments.**",
                ephemeral=True
            )
            return False

        if interaction.guild and interaction.guild.unavailable:
            try:
                await response.send(
                    interaction,
                    content="**This server is unavailable. This is a discord issue.**",
                    ephemeral=True
                )
            except discord.HTTPException:
                pass
            
            return False
        
        data: Namespace[str, Namespace[str, Any]] = Namespace(interaction.data) if interaction.data else Namespace() # type: ignore

        if interaction.command:
            options: InteractionOptions = interaction.command.extras.get('options', InteractionOptions())
        else:
            options: InteractionOptions = interaction.extras.get('options', InteractionOptions())

        if not options.modal_response and options.defer_options.defer:
            await interaction.response.defer(ephemeral=options.defer_options.ephemeral, thinking=options.defer_options.thinking)

        tasks: Namespace[str, Optional[asyncio.Task[Any]]] = Namespace(chunk_guild=None, fetch_league_data=None)

        if interaction.guild:
            if not interaction.guild.chunked:
                tasks.chunk_guild = create_logged_task(
                    asyncio.shield(interaction.guild.chunk())
                )

                if not options.modal_response and not options.defer_options.defer:
                    await interaction.response.defer(ephemeral=options.defer_options.ephemeral, thinking=options.defer_options.thinking)

            if options.league_data.retrieve:
                tasks.fetch_league_data = create_logged_task(
                    asyncio.shield(self.client.database.produce_league(interaction.guild.id, keys=options.league_data.keys))
                )

        player_ids: Set[int] = set()
        if options.player_data.retrieve:
            interaction.extras['players'] = {}
            player_ids.add(interaction.user.id)

            if data.has('resolved'):
                for user_id, discord_user_data in (data.resolved.get('members') or data.resolved.get('users', {})).items():
                    if interaction.user.id == int(user_id) or discord_user_data.get('bot', False) or discord_user_data.get('user', {}).get('bot', False):
                        continue

                    player_ids.add(int(user_id))

        if any(tasks.values()) or player_ids:
            try:
                async with asyncio.timeout(15 if interaction.response.is_done() else 1.5):
                    if tasks.fetch_league_data:
                        fetch_league_data_task, _ = await asyncio.wait([tasks.fetch_league_data], timeout=None)
                        interaction.extras['league'] = fetch_league_data_task.pop().result()

                    if player_ids:
                        results, _ = await asyncio.wait([
                            create_logged_task(
                                asyncio.shield(self.client.database.produce_player(x, interaction.extras['league'])))
                                for x in player_ids
                        ], timeout=None, return_when=asyncio.ALL_COMPLETED)

                    if tasks.chunk_guild:
                        await asyncio.wait([tasks.chunk_guild], timeout=None)

                if player_ids:
                    for player_task in results: # type: ignore  # results is not unbound because its set when player_ids is not empty
                        player = player_task.result()
                        interaction.extras['players'][player.id] = player
                        
            except asyncio.TimeoutError:
                logger.warning(f"Timeout while fetching data for interaction {interaction.id} in guild {interaction.guild.id if interaction.guild else 'DM'}")
                return False

        return True

    async def on_error(self, interaction: discord.Interaction[Bot], error: Exception) -> None:
        await response.send(interaction, content=f"```py\n{''.join(traceback.format_exception(error))}```", ephemeral=True)
        return None