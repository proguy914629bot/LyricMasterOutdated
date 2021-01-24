import discord
import os
os.chdir('/home/gilb/LyricMaster/')
from discord.ext import commands
import json
import logging
import collections
import random
import motor.motor_asyncio
from pathlib import Path
import os
import asyncio
import aiohttp
import json, asyncio
import copy
import traceback
import sys
from collections import Counter, deque, defaultdict

import config
import asyncpg
#import dns

class Document:
    def __init__(self, connection, document_name):
        """
        Our init function, sets up the conenction to the specified document
        Params:
         - connection (Mongo Connection) : Our database connection
         - documentName (str) : The document this instance should be
        """
        self.db = connection[document_name]
        self.logger = logging.getLogger(__name__)

    # <-- Pointer Methods -->
    async def update(self, dict):
        """
        For simpler calls, points to self.update_by_id
        """
        await self.update_by_id(dict)

    async def get_by_id(self, id):
        """
        This is essentially find_by_id so point to that
        """
        return await self.find_by_id(id)

    async def find(self, id):
        """
        For simpler calls, points to self.find_by_id
        """
        return await self.find_by_id(id)

    async def delete(self, id):
        """
        For simpler calls, points to self.delete_by_id
        """
        await self.delete_by_id(id)

    # <-- Actual Methods -->
    async def find_by_id(self, id):
        """
        Returns the data found under `id`
        Params:
         -  id () : The id to search for
        Returns:
         - None if nothing is found
         - If somethings found, return that
        """
        return await self.db.find_one({"_id": id})

    async def delete_by_id(self, id):
        """
        Deletes all items found with _id: `id`
        Params:
         -  id () : The id to search for and delete
        """
        if not await self.find_by_id(id):
            return

        await self.db.delete_many({"_id": id})

    async def insert(self, dict):
        """
        insert something into the db
        Params:
        - dict (Dictionary) : The Dictionary to insert
        """
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        await self.db.insert_one(dict)

    async def upsert(self, dict):
        """
        Makes a new item in the document, if it already exists
        it will update that item instead
        This function parses an input Dictionary to get
        the relevant information needed to insert.
        Supports inserting when the document already exists
        Params:
         - dict (Dictionary) : The dict to insert
        """
        if await self.__get_raw(dict["_id"]) != None:
            await self.update_by_id(dict)
        else:
            await self.db.insert_one(dict)

    async def update_by_id(self, dict):
        """
        For when a document already exists in the data
        and you want to update something in it
        This function parses an input Dictionary to get
        the relevant information needed to update.
        Params:
         - dict (Dictionary) : The dict to insert
        """
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$set": dict})

    async def unset(self, dict):
        """
        For when you want to remove a field from
        a pre-existing document in the collection
        This function parses an input Dictionary to get
        the relevant information needed to unset.
        Params:
         - dict (Dictionary) : Dictionary to parse for info
        """
        # Check if its actually a Dictionary
        if not isinstance(dict, collections.abc.Mapping):
            raise TypeError("Expected Dictionary.")

        # Always use your own _id
        if not dict["_id"]:
            raise KeyError("_id not found in supplied dict.")

        if not await self.find_by_id(dict["_id"]):
            return

        id = dict["_id"]
        dict.pop("_id")
        await self.db.update_one({"_id": id}, {"$unset": dict})

    async def increment(self, id, amount, field):
        """
        Increment a given `field` by `amount`
        Params:
        - id () : The id to search for
        - amount (int) : Amount to increment by
        - field () : field to increment
        """
        if not await self.find_by_id(id):
            return

        await self.db.update_one({"_id": id}, {"$inc": {field: amount}})

    async def get_all(self):
        """
        Returns a list of all data in the document
        """
        data = []
        async for document in self.db.find({}):
            data.append(document)
        return data

    # <-- Private methods -->
    async def __get_raw(self, id):
        """
        An internal private method used to eval certain checks
        within other methods which require the actual data
        """
        return await self.db.find_one({"_id": id})

def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    
    # traverse in the string   
    for ele in s:  
        str1 += f"- `{ele}`\n"

    # return string   
    return str(str1)

class EmbedHelpCommand(commands.HelpCommand):

    def COLOUR(self):
        if self.context.author.color.value == 0:
            num = random.randrange(1, 3)
            if num == 1:
                return discord.Color.random()
            else:
                return discord.Color.blue() 
        else: 
            return self.context.author.color

    def get_ending_note(self):
        return 'Use {0}{1} [command] for more info on a command.\nYou can also do {0}{1} [category] for more info on a category.'.format(self.clean_prefix, self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)

    async def send_bot_help(self, mapping):
        embed = discord.Embed(title='Bot Commands', colour=self.COLOUR())
        description = self.context.bot.description
        if description:
            embed.description = f"{description}"

        for cog, commands in mapping.items():
            name = 'No Category:' if cog is None else f'{str(cog.qualified_name).replace("_", " ").title()}:'
            name += "\n" if cog == False and cog.description == False else ""
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '\n'.join('lm?' + str(c.name) for c in commands)
                if cog and cog.description:
                    value = '{0}\n\n{1}'.format(cog.description, value)

                value += "\n\n--------------\n"

                embed.add_field(name=str(name).replace("Music:", "Music:\n"), value=value, inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(title=f'{str(cog.qualified_name).replace("_", " ").title()} Commands', colour=self.COLOUR())
        if cog.description:
            embed.description = cog.description

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_command(self, command):
        embed = discord.Embed(
            color = self.COLOUR()
        )
        embed.title = f"{str(command.qualified_name).title()} Command"
        embed.description = f'{command.short_doc}' or ''
        embed.add_field(
            name = "Usage:",
            value = f"lm?{str(self.get_command_signature(command))}"
        )
        try:
            embed.add_field(
                name = f'{str(len(command.aliases))} Aliases:' if len(command.aliases) >= 2 else f"{str(len(command.aliases))} Alias:", value = f'{listToString(command.aliases) if listToString(command.aliases) != "" else "No Aliases Found."}', inline = False
            )
        except:
            embed.add_field(
                name = "Aliases:", value = 'No Aliases Found.' 
            )
        embed.add_field(
            name = "In Cog:", value = str(command.cog_name) if command.cog_name != None or command.cog_name != "" else "Comamnd is not in a cog!", inline = False
        )
        try:
            embed.add_field(
                name = "Cooldown:",
                value = f"""
Seconds: {str(command._buckets._cooldown.per).replace(".0", "")}s
How many commands can be runned before the cooldown hits: {str(command._buckets._cooldown.rate)}
Type: Each {str(command._buckets._cooldown.type).replace("commands.", "").replace("BucketType.", "").replace("discord", "").replace("ext", "").replace(".", "").title()}
                """,
                #value = f"{str(command._buckets._cooldown)}s" if command.cooldown != 0.0 else "No Cooldown for this Command!",
                inline = False
            )
        except:
            embed.add_field(
                name = "Cooldown:",
                value = f"""
Seconds: 0s
                """,
                inline = False
            )
        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(title=f"""
{str(group.qualified_name).title()}
        """, colour=self.COLOUR())
        if group.help:
            embed.description = f"{group.help}\n\n"

        if isinstance(group, commands.Group):
            filtered = await self.filter_commands(group.commands, sort=True)
            for command in filtered:
                embed.add_field(name=self.get_command_signature(command), value=command.short_doc or '...', inline=False)

        embed.set_footer(text=self.get_ending_note())
        await self.get_destination().send(embed=embed)

    send_command_help = send_command

def reaadmemberprefix(bot, message):
    with open('ImportantFiles/memberprefix.json', 'r') as f:
        memberprefix = json.load(f)

    memberprefixes = memberprefix[str(message.author.id)]
    return str(memberprefixes)

def readguildprefix(bot, message):
    with open('ImportantFiles/guildprefix.json', 'r') as f:
        guildprefix = json.load(f)

    guildprefixes = guildprefix[str(message.guild.id)]
    return str(guildprefixes)

with open('BotRecords/BotInfo.json', 'r') as f:
    secret_file = json.load(f)

extensions = (
    'cogs.music',
    #'cogs.version',
    'cogs.error',
    #'cogs.prefix',
    #'cogs.misc',
    #'cogs.recordcmd',
    'cogs.botrelated',
    'cogs.moderation',
    'cogs.fun',
    #'cogs.invites',
    #'cogs.reaction',
    #'cogs.economybot',
    #'cogs.mystbin',
    #'cogs.security',
    #'cogs.tag',
    #'cogs.channel',
    #'cogs.snipe',
    'cogs.rtfm',
    #'cogs.tag',
    #'cogs.giveaway',
    'cogs.exec',
    #'cogs.github',
    'cogs.guildevents',
    #'cogs.ServerStats'
    'cogs.emoji',
    'cogs.help'
)

description = """
Hello! I am LyricMaster. To see my commands, you can do \"lm?help\"!
"""

class LyricMaster(commands.AutoShardedBot):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix = commands.when_mentioned_or(
                'lm!', 
                '!lm ', 
                '?lm ', 
                'lm?', 
                '!lm', 
                '?lm'
            ), 
            description = description, 
            #help_command = EmbedHelpCommand(), 
            intents = intents, 
            case_insensitive = True, 
            owner_id = 699839134709317642
        )
        self.config_token = secret_file.get("token")
        self.github_token = secret_file.get("github-key")
        self.connection_url = secret_file.get("mongo")
        self.joke_api_key = secret_file.get("rapidapi-key")
        #self.session = aiohttp.ClientSession(loop=self.loop)
        #self.blacklisted_users = []

        for ext in extensions:
            self.load_extension(ext)

        self.load_extension("jishaku")

        self.description = """
Hello! I am LyricMaster. To see my commands, you can do \"lm?help\"!
        """
    
    async def on_ready(self):
        self.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(self.connection_url))
        self.db = self.mongo["LyricMaster"]
        self.config = Document(self.db, "config")
        self.reaction_roles = Document(self.db, "reaction_roles")

        print(f'Initialized Mongo Database\n')

        await self.change_presence(status=discord.Status.online, activity=discord.Activity(type = discord.ActivityType.playing, name = '🎵 Prefix: "lm?" 🎶', large_image_url = "https://cdn.discordapp.com/attachments/792327068398125077/794068939989712906/LyricMaster.jpg"))
        print(f'{self.user} is logged in and ready to use!\n')

    def run(self):
        super().run(str(self.config_token))

if __name__ in "__main__":
    bot = LyricMaster()
    bot.run()

#def read_json(filename):
#    with open(f"BotRecords/{filename}.json", "r") as f:
#        data = json.load(f)
#    return data

#def write_json(data, filename):
#    with open(f"BotRecords/{filename}.json", "w") as f:
#        json.dump(data, f, indent=4)

#@bot.event
#async def on_message(message):
#    if message.author.id in bot.blacklisted_users:
#        return
#
#    await bot.process_commands(message)

#@bot.command()
#@commands.is_owner()
#async def blacklist(ctx, user: discord.User, reason = None):
#    if user.id == ctx.message.author.id:
#        await ctx.send("Hey, you cannot blacklist yourself!")
#        return
#
#    if user.id == bot.id:
#        await ctx.send(f"You cannot blacklist me bruh...")
#        return
#
#    bot.blacklisted_users.append(user.id)
#    data = read_json("blacklist")
#    if user.id in data["blacklistedUsers"]:
#        await ctx.send(f'`{user.name}#{user.discriminator}` with ID {user.id} is already blacklisted!')
#        return
#
#    data["blacklistedUsers"].append(user.id)
#    write_json(data, "blacklist")
#    if reason == None:
#        reason = "Reason Not Given!"
#    try:
#        await user.send(f"""
#Hey, I got some little bad news for you...
#
#Dear {user.name}#{user.discriminator},
#
#We do not knwo how we can tell you this but, You have been blacklisted by {ctx.author} with the Reason: {reason}. If you think that this is a mistake, contact support by contacting <@699839134709317642> --> proguy914629#5419!
#
#Thanks!
#
#Best Regards,
#{bot.user}.
#        """)
#    except:
#        await ctx.send('Cannot send messages to user, passing this mode and moving into blacklisting user.')
#    
#    await asyncio.sleep(5)
#
#    await ctx.send(f'Blacklisted `{user.name}#{user.discriminator}` with ID {user.id}!')
#
#@bot.command()
#@commands.is_owner()
#async def unblacklist(ctx, user: discord.User, reason = None):
#    data = read_json("blacklist")
#
#    if str(user.id) not in data["blacklistedUsers"]:
#        await ctx.send(f'`{user.name}#{user.discriminator}` with ID {user.id} is not blacklisted!')
#        return
#
#    bot.blacklisted_users.remove(user.id)
#    data["blacklistedUsers"].remove(user.id)
#    write_json(data, "blacklist")
#    await ctx.send(f"Okay, I have unblacklisted `{user.name}#{user.discriminator}` with ID {user.id} for you.")

#if __name__ in '__main__':
#
#    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(bot.connection_url))
#    bot.db = bot.mongo["LyricMaster"]
#    bot.config = Document(bot.db, "config")
#    bot.reaction_roles = Document(bot.db, "reaction_roles")
#    print(f'Initialized Mongo Database\n')
#
#    for ext in extensions:
#        bot.load_extension(ext)
#
#    bot.load_extension("jishaku")
#    
#
#bot.run(str(bot.config_token))
