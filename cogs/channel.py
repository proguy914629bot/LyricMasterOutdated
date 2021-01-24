import discord
from discord.ext import commands

class Channel_And_VC(commands.Cog): #PLAN: Do like VoiceMaster
    """
    Channel and VC Commands... For playing and skipping music commands, see the Music Commands by doing \"lm?help music\"!
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        print(str(before))
        print("------------------------------")
        print(str(after))

def setup(bot):
    bot.add_cog(Channel_And_VC(bot))
    print("Channel And VC Cog Is Ready!")