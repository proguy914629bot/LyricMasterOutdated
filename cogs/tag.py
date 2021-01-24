import discord
from discord.ext import commands
import json
import asyncio
import os
import datetime
from datetime import date

os.chdir("/home/gilb/LyricMaster/")

class Tag(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.TagNotFound = "Tag {} Not Found!"

    @commands.group()
    @commands.guild_only()
    async def tag(self, ctx, TagName = None):
        """Tag Command. See info using help command...
        """
        #if str(TagName).startswith("-"):
        #    if ctx.invoked_subcommand is None:
        #        await self.bot.get_command(ctx, 'tag')
        #        await ctx.send("If this is what you didn't expect, please contact `proguy914629#5419`!")
        #        return

        #if TagName == None:
        #    if ctx.invoked_subcommand is None:
        #        await self.bot.get_command(ctx, 'tag')
        #        return

        #if ctx.invoked_subcommand is None:
        #    await ctx.send("Something wen't wrong. Try again in a few moments!")
        #    return

        with open("BotRecords/tag.json", "r") as f:
            loadtag = json.load(f)
        try:
            if str(TagName) not in loadtag[str(ctx.guild.id)]:
                await ctx.send(self.TagNotFound.format(TagName))
                return

            await ctx.send(str(loadtag[str(ctx.guild.id)][str(TagName)]["Response"]))

            if "Stats" not in loadtag[str(ctx.guild.id)][str(TagName)]:
                loadtag[str(ctx.guild.id)][str(TagName)]["Stats"] = 1
            else:
                loadtag[str(ctx.guild.id)][str(TagName)]["Stats"] += 1

            with open("BotRecords/tag.json", "r") as f:
                json.dump(loadtag, f, indent=4)
        except KeyError:
            pass

    @tag.command(aliases = ['--create', '-create', '--mktag', '-mktag', '--maketag', '-maketag', '--addtag', '-addtag', '--createtag', '-createtag'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def tag_create(self, ctx, *, name):
        if str(name).startswith("-"):
            await ctx.send("For specific purposes only, you may not put a `-` as what your tag startswith as it will tell me that the tag is a function!")
            return

        with open("BotRecords/tag.json", "r") as f:
            data = json.load(f)
        try:
            if str(name) in data[str(ctx.guild.id)]:
                await ctx.send("That is already a valid tag!")
                return
        except KeyError:
            pass

        embed1 = discord.Embed(
            title = "The name of the tag will be {}! Say `confirm` to continue or say `cancel` to leave.".format(name),
            color = ctx.author.color
        )
        await ctx.send(embed=embed1)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send("Took to long. Try again later!")
            return

        finalmsg1 = str(msg.content).lower()

        if finalmsg1 == "confirm":
            await ctx.send("Okay!")
        elif finalmsg1 == "cancel":
            await ctx.send("Okay! Cancelled!")
            return
        else:
            await ctx.send("Answer {} not accepted!".format(finalmsg1))
            return

        await ctx.send("What should be the response of the tag?\n\nTip: Instead of pysical Enter/Return buttons, you can just type NewLineTable. `This is case sensitive...`")

        response = await self.bot.wait_for('message', check=check)

        if str(response.content).lower() == "cancel":
            await ctx.send("Okay! Cancelled!")
            return

        finalresponse = str(response.content).replace("NewLineTable", "\n")

        await ctx.send("Here is a final total of the content. Say `confirm` to make it an official tag or say `cancel` to cancel!\n\n{}".format(finalresponse))

        try:
            msg2 = await self.bot.wait_for('message', check=check, timeout = 60.0)
        except asyncio.TimeoutError:
            await ctx.send("Took to long. Try again later!")
            return

        finalmsg2 = str(msg2.content).lower()

        if finalmsg2 == "confirm":
            await ctx.send("Okay!")
        elif finalmsg2 == "cancel":
            await ctx.send("Okay! Cancelled!")
            return
        else:
            await ctx.send("Answer {} not accepted!".format(finalmsg1))
            return

        todayDate = datetime.datetime.now()

        finalTodayDate = todayDate.strftime("%A, %d %B %Y %I:%M %p")

        guild = str(ctx.guild.id)

        data[guild][str(name)] = {}
        data[guild][str(name)]["TimeCreated"] = str(finalTodayDate)
        data[guild][str(name)]["Response"] = f'{str(finalresponse)} UTC'
        data[guild][str(name)]["TagStatus"] = "MainTag"
        data[guild][str(name)]["CreatedByID"] = str(ctx.author.id)
        #data[guild][str(name)][""]

        with open("BotRecords/tag.json", "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send("Tag Sucsessfully created! You can launch the info command on that tag, Or run that tag and see if everything has gone well!")

    @tag.command(aliases = ['--info', '-info'])
    @commands.guild_only()
    async def tag_info(self, ctx, TagName):
        with open("BotRecords/tag.json", "r") as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            await ctx.send("Bruh, you haven't even set a tag yet!")
            return

        guild = str(ctx.guild.id)

        if data[guild][str(TagName)]["TagStatus"] == "Alias":
            TagName = data[guild][str(TagName)]["MainStatus"]

        embed = discord.Embed(
            title = f"Tag Info - {str(TagName)}",
            color = ctx.author.color,
            timestamp = ctx.message.created_at
        )
        embed.add_field(
            name = "Main Tag Name:",
            value = f"{TagName}",
            inline = False
        )

def setup(bot):
    bot.add_cog(Tag(bot))