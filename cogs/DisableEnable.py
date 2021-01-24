import discord
import json
from discord.ext import commands
import os

os.chdir("/home/gilb/LyricMaster/BotRecords/")

class CommandManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def command_check(self, ctx : commands.Context) -> bool:
        

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def enable(self, ctx):
        