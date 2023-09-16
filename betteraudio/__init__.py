from redbot.core.bot import Red
from .betteraudio import BetterAudio

async def setup(bot: Red):
    if bot.get_cog("Audio"):
        print("Audio is loaded, attempting to add to or override its commands")
    await bot.add_cog(BetterAudio(bot))