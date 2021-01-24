import discord
from discord.ext import commands

class Error(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    
  @commands.Cog.listener()
  async def on_command_error(self,ctx,error):
    if isinstance(error,commands.CommandNotFound):
      command = str(ctx.message.content).replace("!lm ", "").replace("?lm ", "").replace("lm", "").replace("?", "").replace("<@!755291533632077834>", "").replace("<@755291533632077834>", "").replace("!", "").split(" ")[0]
      await ctx.send(f'Command `{str(command)}` Not Found!')
      return
    elif isinstance(error, commands.CommandOnCooldown):
      await ctx.send(error)
    elif isinstance(error, commands.MemberNotFound):
      await ctx.send(f'Member Not Found!')
      return
    elif isinstance(error, commands.ChannelNotFound):
      await ctx.send(f'Channel Not Found!')
      return
    elif isinstance(error, commands.MissingRequiredArgument):
      await ctx.send(error)
      return
    elif isinstance(error, commands.MissingPermissions):
      await ctx.send(error)
    elif isinstance(error, commands.NoPrivateMessage):
      await ctx.send('Bruh. I ony work in servers. Not DM\'s. Try again but next time, do it in a server!')
      return
    elif isinstance(error, commands.NotOwner):
      await ctx.send("You have no permissions to run this command! Only the owner can run the command!")
      return
    elif isinstance(error, commands.EmojiNotFound):
      await ctx.send(error)
      return
    else:
      await ctx.send('Something wen\'t unexpectedly wrong! We have alerted the developers!\n{}'.format(error))
      raise error
            
def setup(bot):
  bot.add_cog(Error(bot))
  print('Error Handling Cog Is Ready!')
