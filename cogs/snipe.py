import os
import discord
from discord.ext import commands
import json

os.chdir("/home/gilb/LyricMaster/")

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        with open("BotRecords/snipe.json", "r") as f:
            data = json.load(f)

        data[str(message.guild.id)] = {}
        data[str(message.guild.id)]["Message"] = str(message.content)
        data[str(message.guild.id)]["AuthorName"] = f'{str(message.author.name)}#{str(message.author.discriminator)}'
        data[str(message.guild.id)]["AuthorID"] = str(message.author.id)
        data[str(message.guild.id)]["ChannelName"] = str(message.channel.name)
        data[str(message.guild.id)]["ChannelID"] = str(message.channel.id)

        with open("BotRecords/snipe.json", "w") as f:
            json.dump(data, f, indent=4)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild == None and after.guild == None:
            return

        if after.edited_at is None:
            return
        
        with open("BotRecords/snipeedit.json", "r") as f:
            data = json.load(f)

        message = after

        data[str(message.guild.id)] = {}
        data[str(message.guild.id)]["BeforeContent"] = str(before.content)
        data[str(message.guild.id)]["AfterContent"] = str(after.content)
        data[str(message.guild.id)]["AuthorName"] = f'{str(message.author.name)}#{str(message.author.discriminator)}'
        data[str(message.guild.id)]["AuthorID"] = str(message.author.id)
        data[str(message.guild.id)]["ChannelName"] = str(message.channel.name)
        data[str(message.guild.id)]["ChannelID"] = str(message.channel.id)

        with open("BotRecords/snipe.json", "w") as f:
            json.dump(data, f, indent=4)

    async def snipe_delete(self, ctx):
        with open("BotRecords/snipe.json", "r") as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            await ctx.send('There is nothing to snipe!')
            return

        messageContent = str(data[str(ctx.guild.id)]["Message"])
        authorName = str(data[str(ctx.guild.id)]["AuthorName"])
        authorID = str(data[str(ctx.guild.id)]["AuthorID"])
        channelName = str(data[str(ctx.guild.id)]["ChannelName"])
        channelID = str(data[str(ctx.guild.id)]["ChannelID"])

        finalAuthor = await self.bot.fetch_user(int(authorID))
        finalChannel = ctx.guild.get_channel(int(channelID))
        categoryName = str(finalChannel.category)
        embed = discord.Embed(
            title = 'Snipe/Most recent message deleted in this guild:',
            description = f'''
Message: {messageContent if messageContent != "" else '`UNKNOWN! Cannot Display More Details. Probably because the message deleted is an Embed! Ask support for more details!`'}
Author/Person Who Deleted Message: {finalAuthor.mention} | `{authorName}`
In Channel: {finalChannel.mention} | `{channelName}`
Category: `{categoryName}`
            ''',
            timestamp = ctx.message.created_at,
            color = ctx.author.color
        )
        await ctx.send(embed=embed)

    async def snipe_edit(self, ctx):
        with open("BotRecords/snipeedit.json", "r") as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            await ctx.send('There is nothing to snipe!')
            return

        messageContentBefore = str(data[str(ctx.guild.id)]["BeforeContent"])
        messageContentAfter = str(data[str(ctx.guild.id)]["AfterContent"])
        authorName = str(data[str(ctx.guild.id)]["AuthorName"])
        authorID = str(data[str(ctx.guild.id)]["AuthorID"])
        channelName = str(data[str(ctx.guild.id)]["ChannelName"])
        channelID = str(data[str(ctx.guild.id)]["ChannelID"])

        finalAuthor = await self.bot.fetch_user(int(authorID))
        finalChannel = ctx.guild.get_channel(int(channelID))
        categoryName = str(finalChannel.category)

        embed = discord.Embed(
            title = 'Snipe Edit/Most recent message edited in this guild:',
            description = f'''
Message Content (Before): {messageContentBefore if messageContentBefore != "" else '`UNKNOWN! Cannot Display More Details. Probably because the message deleted is an Embed! Ask support for more details!`'}
Message Content (After): {messageContentAfter if messageContentAfter != "" else '`UNKNOWN! Cannot Display More Details. Probably because the message deleted is an Embed! Ask support for more details!`'}
Author/Person Who Deleted Message: {finalAuthor.mention} | `{authorName}`
In Channel: {finalChannel.mention} | `{channelName}`
Category: `{categoryName}`
            ''',
            timestamp = ctx.message.created_at,
            color = ctx.author.color
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def snipe(self, ctx, mode = None):
        if mode != None:
            if mode != "edit":
                return await self.snipe_delete(ctx)
            else:
                return await self.snipe_edit(ctx)
        else:
            return await self.snipe_delete(ctx)

def setup(bot):
    bot.add_cog(Snipe(bot))
    print('Snipe Cog Is Ready!')