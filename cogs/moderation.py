import discord
import json
from discord.ext import commands
import os
import json
from discord.ext import flags

os.chdir("/home/gilb/LyricMaster/")

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #@commands.command()
    async def warn(self, ctx, member : discord.Member = None, reason = "Not Given"):
        if member == None:
            await ctx.send("Please mention a member's ID or Name as anm argument!")
            return

        with open("BotRecords/warn.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)][str(member.id)] = {}
        data[str(ctx.guild.id)][str(member.id)]["Count"] += 1

        with open("BotRecords/warn.json", "w") as f:
            json.dump(data, f, indent=4)

        with open("BotRecprds/warn.json", "r") as fi:
            datas = json.load(fi)

        datas[str(ctx.guild.id)][str(member.id)]["Warn"] = {}
        datas[str(ctx.guild.id)][str(member.id)]["Warn"][datas[str(ctx.guild.id)][str(member.id)]["Count"]] = {}
        datas[str(ctx.guild.id)][str(member.id)]["Warn"][datas[str(ctx.guild.id)][str(member.id)]["Count"]]["Reason"] = reason
        datas[str(ctx.guild.id)][str(member.id)]["Warn"][datas[str(ctx.guild.id)][str(member.id)]["Count"]]["Mod"] = {}
        datas[str(ctx.guild.id)][str(member.id)]["Warn"][datas[str(ctx.guild.id)][str(member.id)]["Count"]]["Mod"]["Name"] = f"{ctx.author.name}#{ctx.author.discriminator}"
        datas[str(ctx.guild.id)][str(member.id)]["Warn"][datas[str(ctx.guild.id)][str(member.id)]["Count"]]["Mod"]["ID"] = ctx.author.id

        with open("BotRecords/warn.json", "w") as fi:
            json.dump(datas, fi, indent=4)

        with open("BotRecords/warn.json", "r") as fil:
            warns = json.load(fil)

        try:
            await member.send(f'You have been warned by {ctx.author.name}#{ctx.author.discriminator} in {ctx.guild.name}.\nReason: {str(reason)}')
        except:
            pass

        if warns[str(ctx.guild.id)][str(member.id)]["Count"] == 1:
            return await ctx.send(f"Okay! {str(member.name)}#{str(member.discriminator)}. Reason: {str(reason)}. It is now their 1st Warning!")
        elif warns[str(ctx.guild.id)][str(member.id)]["Count"] == 2:
            return await ctx.send(f"Okay! {str(member.name)}#{str(member.discriminator)}. Reason: {str(reason)}. It is now their 2nd Warning!")
        elif warns[str(ctx.guild.id)][str(member.id)]["Count"] == 3:
            return await ctx.send(f"Okay! {str(member.name)}#{str(member.discriminator)}. Reason: {str(reason)}. It is now their 3rd Warning!")
        else:
            return await ctx.send(f'Okay! {str(member.name)}#{str(member.discriminator)}. Reason: {str(reason)}. It is now their {warns[str(ctx.guild.id)][str(member.id)]["Count"]}th Warning!')

    @flags.add_flag("--channel", type=discord.TextChannel, default=None)
    @flags.add_flag("--member", type=discord.Member, default=None)
    @flags.add_flag("--amount", default=0)
    @flags.add_flag("--oldest", type=bool, default=False)
    @commands.command(aliases = ['purge'], cls=flags.FlagCommand)
    @commands.bot_has_guild_permissions(manage_messages=True)
    async def clear(self, ctx, **flags):
        amount = flags["amount"]
        channel = flags["channel"]
        member = flags['member']
        oldest = flags['oldest']

        if channel == None:
            channel = ctx.channel

        if amount == 0:
            return await ctx.send("Cannot Purge messages because amount is either not a valid argument or amount is 0!")
        
        if member == None:
            membercheck = False
            deleted = await channel.purge(limit=int(amount), oldest_first=oldest)
        else:
            membercheck = True
            def check(m):
                return m.author == member

            deleted = await channel.purge(limit=int(amount), oldest_first=oldest, check=check)

        embed = discord.Embed()
        if len(deleted) == 1:
            embed.title = "Deleted 1 Message"
        else:
            embed.title = "Deleted {} Messages".format(len(deleted))
        
        desc = f"""
**Checks:**

Oldest First: {str(oldest)}
Member Check: {str(membercheck)}
        """
        if membercheck == True:
            desc += """Member: `{}`
            """.format(str(member))
        
        embed.description = desc

        await ctx.send(embed=embed)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, discord.Forbidden):
            return await ctx.send("You do not have the permissions to purge/clear messages!")
        elif isinstance(error, discord.HTTPException):
            return await ctx.send("Soomething wen't wrong when purging/clearing the messages. Try again in a few moments!")
        elif isinstance(error, commands.BotMissingPermissions):
            return await ctx.send("I am missing the `manage messages` permission!")

def setup(bot):
    bot.add_cog(Moderation(bot))
    print("Moderation Cog Is Ready")