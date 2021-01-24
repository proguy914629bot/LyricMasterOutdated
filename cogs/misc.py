import discord
from discord.ext import commands
from discord.utils import oauth_url as oauth2

class Misc(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
      
def setup(bot):
  bot.add_cog(Misc(bot))
  print('Misc Cog Is Ready!')