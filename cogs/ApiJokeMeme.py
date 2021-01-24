import discord
from aiohttp import ClientSession
from discord.ext import commands

class API(commands.Cog):
    def __init__(self,bot):
        self.bot = bot

    @commands.command(
        aliases = ['dadjokes']
    )
    async def dadjoke(self, ctx):
        url = ""

        headers = {}

        

def setup(bot):
    bot.add_cog(API(bot))