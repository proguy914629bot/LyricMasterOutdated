import discord
from discord.ext import commands
import akinator

class Akinator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(
        aliases = ['aki']
    )
    async def akinator(self, ctx, mode = "NonNSFW", lang = "en"):
        aki = akinator.Akinator()
        finalmode = mode.lower()
        if finalmode == "nonnsfw":
            q = aki.start_game(language=str(lang), child_mode=True)
        else:
            q = aki.start_game(child_mode=False, language=str(lang))

def setup(bot):
    bot.add_cog(Akinator(bot))