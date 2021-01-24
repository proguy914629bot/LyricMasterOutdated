import discord
from discord.ext import commands
import os
import json
import asyncio
import random

class Versions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        msg = message
        if str(message.content).startswith("lm!"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return
        if str(message.content).startswith("!lm"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return
        if str(message.content).startswith("lm?"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return
        if str(message.content).startswith("?lm"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return
        if str(message.content).startswith("<@755291533632077834>"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return
        if str(message.content).startswith("<@!755291533632077834>"):
            with open('BotRecords/version.json', 'r') as f:
                data = json.load(f)

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            if data[str(msg.guild.id)] != datas["UpToDateVersion"]:
                await msg.channel.send(f'Your version is up to date! Version {data[str(msg.guild.id)]}')
                return

    @commands.command()
    async def whatsnew(self, ctx, version = None):
        with open("BotRecords/version.json", "r") as f:
            data = json.load(f)

        if version == None:
            version = str(data[str(ctx.guild.id)])

        if str(version) not in data:
            await ctx.send("That version has not been recorded yet.")
            return

        await ctx.send(str(data[str(version)]))        

    @commands.command()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator = True)
    async def update(self, ctx):
        with open('BotRecords/version.json', 'r') as f:
            data = json.load(f)

        with open('BotRecords/currentversion.json', 'r') as fp:
            datas = json.load(fp)

        if data[str(ctx.guild.id)] == datas["UpToDateVersion"]:
            await ctx.send(f'Your version is up to date! Version {data[str(ctx.guild.id)]}')
            return

        await ctx.send(f'STATUS: Upgrading from Version {data[str(ctx.guild.id)]} to Version {datas["UpToDateVersion"]}!')

        data[str(ctx.guild.id)] = datas["UpToDateVersion"]

        with open('BotRecords/version.json', 'r') as f:
            json.dump(data, f, indent=4)

        await asyncio.sleep(random.randrange(5, 15))

        await ctx.send('STATUS: Restaring bot. Note that commands will work and still play music but bot will be on Safe Mode only for this guild to update.\nCurrent Playing Music (If you are) might lag a little... \n\nThis will take maximum 10 seconds! Please wait...')

        await asyncio.sleep(random.randrange(5, 10))

        with open('BotRecords/version.json', 'w') as f:
            json.dump(data, f, indent=4)

        with open('BotRecords/version.json', 'r') as f:
            data2 = json.load(f)

        await ctx.send(f'Thanks for updating and using the bot! Bot version updated to {str(data2[str(ctx.guild.id)])}!\nWhat\'s New: \nRun the command `lm?whatsnew` to see what\'s new in this version!')

    @commands.command()
    @commands.is_owner()
    async def setcurrentversion(self, ctx, *, currentversion = None):
        if currentversion == None:
            await ctx.send('Please put a valid version number!')
            return

        with open('BotRecords/version.json', 'r') as f:
            data = json.load(f)
        if "UpToDateVersion" in data:
            if str(currentversion) == data["UpToDateVersion"]:
                await ctx.send("That is the current version that was set before!")
                return
            else:
                pass
        else:
            pass

        data["UpToDateVersion"] = str(currentversion)

        with open('BotRecords/version.json', 'w') as f:
            json.dump(data, f, indent=4)

        await ctx.send(f'Okay! Up To Date Version has been set to: {currentversion}!')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open('BotRecords/version.json', 'r') as f:
            data = json.load(f)

        with open('BotRecords/currentversion.json', 'r') as fp:
            datas = json.load(fp)

        data[str(guild.id)] = str(datas["UpToDateVersion"])

        with open('BotRecords/version.json', 'w') as f:
            json.dump(data, f, indent=4)

    @commands.command()
    async def version(self, ctx):
        with open('BotRecords/version.json', 'r') as f:
            data = json.load(f)

        if str(ctx.guild.id) in data:

            await ctx.send(f'Current Bot Version: `{data[str(ctx.guild.id)]}`')
            return

        else:

            with open('BotRecords/currentversion.json', 'r') as fp:
                datas = json.load(fp)

            data[str(ctx.guild.id)] = str(datas["UpToDateVersion"])

            with open('BotRecords/version.json', 'w') as f:
                json.dump(data, f, indent=4)

            await ctx.send(f'Current Bot Version: `{data[str(ctx.guild.id)]}`')

def setup(bot):
    bot.add_cog(Versions(bot))
    print('Version Cog Is Ready!')