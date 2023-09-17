from pathlib import Path

import lavalink
from red_commons.logging import getLogger

from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator

log = getLogger("red.cogs.BlueKorvyd.AudioXtend")

_ = Translator("Audio", Path(__file__))


class AudioXtend(commands.Cog):
    """
    Extension of the Audio cog
    """

    def __init__(self, bot: Red):
        self.bot = bot
        self.audio = bot.get_cog("Audio")

    @commands.command(name="move")
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def command_move(self, ctx: commands.Context, previous_index: int, next_index: int):
        """Move a track to another position of the queue."""
        dj_enabled = self.audio._dj_status_cache.setdefault(
            ctx.guild.id, await self.audio.config.guild(ctx.guild).dj_enabled()
        )
        if not self.audio._player_check(ctx):
            return await self.audio.send_embed_msg(ctx, title=_("Nothing playing."))
        player = lavalink.get_player(ctx.guild.id)
        can_skip = await self.audio._can_instaskip(ctx, ctx.author)
        if (not ctx.author.voice or ctx.author.voice.channel != player.channel) and not can_skip:
            return await self.audio.send_embed_msg(
                ctx,
                title=_("Unable To Move Track"),
                description=_("You must be in the voice channel to move a track."),
            )
        if dj_enabled and not can_skip:
            return await self.audio.send_embed_msg(
                ctx,
                title=_("Unable To Move Track"),
                description=_("You need the DJ role to move tracks."),
            )
        if previous_index > len(player.queue) or previous_index < 1:
            return await self.audio.send_embed_msg(
                ctx,
                title=_("Unable To Move Track"),
                description=_("Previous song number must be greater than 1 and within the queue limit."),
            )
        if next_index < 1:
            next_index = 1
        if next_index > len(player.queue):
            next_index = len(player.queue) 
        player.store("notify_channel", ctx.channel.id)
        real_previous_index = previous_index - 1
        real_next_index = next_index - 1
        move_song = player.queue[real_previous_index]
        move_song.extras["bumped"] = True
        removed = player.queue.pop(real_previous_index)
        player.queue.insert(real_next_index, move_song)
        description = await self.audio.get_track_description(removed, self.audio.local_folder_current_path)
        await self.audio.send_embed_msg(
            ctx, 
            title=_("Moved track to position {next_position} in the queue.").format(next_position=next_index), 
            description=description
        )