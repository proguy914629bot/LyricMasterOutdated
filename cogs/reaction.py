import discord
import typing
import emojis
import os
import asyncio
from discord.ext import commands
import json
from discord.utils import get

os.chdir("/home/gilb/LyricMaster/")

class ReactionRolesNotSetup(Exception):
    """Reaction Roles are not setup for this guild."""
    pass

def is_setup():
    async def wrap_func(ctx):
        data = await ctx.bot.config.find(ctx.guild.id)
        if data is None:
            await ctx.send("Error! You did not set up Reaction Roles yet!")
            #raise ReactionRolesNotSetup({"Error": "You did not set up Reaction Roles yet!"})

        if data.get("message_id") is None:
            await ctx.send("Error! You did not set up Reaction Roles yet!")
            #raise ReactionRolesNotSetup

        return True
    return commands.check(wrap_func)

class Reactions(commands.Cog, name = "Reaction Roles"):
    def __init__(self, bot):
        self.bot = bot

    async def rebuild_role_embed(self, guild_id):
        data = await self.bot.config.find(guild_id)
        channel_id = data['channel_id']
        message_id = data['message_id']

        guild = await self.bot.fetch_guild(guild_id)
        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        with open('BotRecords/reaction.json', 'r') as f:
            reaction = json.load(f)
        
        embed = discord.Embed(
            title = str(reaction[str(guild_id)]["title"]),
            #color = int(str(reaction[str(guild_id)]["color"]).replace("#", "0x")),
            #description = str(reaction[str(guild_id)]["desc"])
        )

        await message.clear_reactions()

        await message.edit(embed=embed)

        reaction_roles = await self.bot.reaction_roles.get_all()
        reaction_roles = list(filter(lambda r: r['guild_id'] == guild_id, reaction_roles))
        for item in reaction_roles:
            await message.add_reaction(item["_id"])

    async def get_current_reactions(self, guild_id):
        data = await self.bot.reaction_roles.get_all()
        data = filter(lambda r: r['guild_id'] == guild_id, data)
        data = map(lambda r: r['_id'], data)

        return list(data)

    @commands.group(
        aliases = ['rr', 'reactionrole'],
        invoke_without_command = True
    )
    @commands.guild_only()
    async def reactionroles(self, ctx):
        embed = discord.Embed(
            title = 'Reaction Roles Commands List:',
            color = ctx.author.color
        )
        embed.add_field(
            name = "Channel:",
            value = """
```
lm?rr channel <Channel>
```\n\n
            """,
            inline = False
        )
        embed.add_field(
            name = "Toggle: Toggles the Reaction Role for this guild.",
            value = """
```
lm?rr toggle
```\n\n
            """,
            inline = False
        )
        embed.add_field(
            name = "Add: Adds a new Reaction Role.",
            value = """
```
lm?rr add <Emoji> <Role>
```\n\n
            """,
            inline = False
        )
        embed.add_field(
            name = "Remove: Remove an existing Reaction Role using it's emoji!",
            value = """
```
lm?rr rm <Emoji>
```\n\n
            """,
            inline = False
        )
        embed.add_field(
            name = "Set: Sets a specific item of the Reaction Role Embed.",
            value = """
```
lm?rr set <Type (Title, Description, Color)> <Message>
```
            """,
            inline = False
        )
        await ctx.send(embed=embed)

    @reactionroles.command(name = "channel")
    @commands.guild_only()
    @commands.has_guild_permissions(manage_channels = True)
    async def rr_channel(self, ctx, channel : discord.TextChannel = None):
        if channel == None:
            await ctx.send(f'Please mention the channel as a second argument! Do it like `lm?rr channel {ctx.channel.mention}` next time!')
            return

        try:
            await ctx.send("Testing Permissions!", delete_after = 0.05)
        except discord.HTTPException:
            await ctx.send(f'I cannot send messages in {channel.name}! Make me have `Embed Links`, `Send Messages` and `Read Messages` permissions and then try again!')
            return

        try:
            embed = discord.Embed(title = "Testing")
            await ctx.send(embed=embed, delete_after = 0.05)
        except discord.HTTPException:
            await ctx.send(f'I cannot send embeds in {channel.name}! Make me have `Embed Links`, `Send Messages`, and `Read Messages` permissions then try again!')
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        questions = [
            'What Should Be The Title of the Embed?',
            'What Should Be The Description of the Embed? Say `none` if you do not want a description!',
        ]

        answers = []

        for i in questions:
            await ctx.send(i)

            try:
                msg = await self.bot.wait_for('message', check=check, timeout = 120.0)
            except asyncio.TimeoutError:
                await ctx.send('Took Too Long. Try Again Later!')
            else:
                answers.append(msg.content)

        #if str(answers[2]) == "none":
        answer = ctx.guild.owner.color

        if str(answer).startswith(("#", "0x")):
            reaction_roles = await self.bot.reaction_roles.get_all()
            reaction_roles = list(filter(lambda r: r['guild_id'] == ctx.guild.id, reaction_roles))
            for item in reaction_roles:
                role = ctx.guild.get_role(item["role"])
                if str(answers[1]) == "none":
                    desc = f"{item['_id']}: {role.mention}"
                else:
                    desc = f"{str(answers[1])}\n\n{item['_id']}: {role.mention}"
            if answer != None:
                finalanswer = answer
                if str(answers[1]) == 'none':
                    embed = discord.Embed(
                        title = str(answers[0]),
                        color = finalanswer
                    )
                else:
                    embed = discord.Embed(
                        title = str(answers[0]),
                        color = finalanswer,
                        description = desc
                    )
            else:
                if answers[1] == "none":
                    embed = discord.Embed(
                        title = str(answers[0])
                    )
                else:
                    embed = discord.Embed(
                        title = str(answers[0]),
                        description = desc
                    )
            with open('BotRecords/reaction.json', 'r') as f:
                reaction = json.load(f)

            reaction[str(ctx.guild.id)] = {}
            reaction[str(ctx.guild.id)]["title"] = str(answers[0])
            #reaction[str(ctx.guild,id)]["desc"] = str(desc)
            reaction[str(ctx.guild.id)]["color"] = str(finalanswer)

            with open('BotRecords/reaction.json', 'w') as f:
                json.dump(reaction, f, indent=4)

        else:
            await ctx.send('That is not a HEX Code. Try again later!')
            return

        m = await channel.send(embed=embed)
        for item in reaction_roles:
            await m.add_reaction(item['_id'])

        await self.bot.config.upsert(
            {
                "_id": ctx.guild.id,
                "message_id": m.id,
                "channel_id": m.channel.id,
                "is_enabled": True,
            }
        )
        await ctx.send('That should be all!', delete_after = 30.0)

    @reactionroles.command(name = "toggle")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @is_setup()
    async def rr_toggle(self, ctx):
        """Toggles the Reaction Role for this guild."""

        data = await self.bot.config.find(ctx.guild.id)

        data["is_enabled"] = not data["is_enabled"]
        await self.bot.config.upsert(data)

        is_enabled = "enabled!" if data["is_enabled"] else "disabled!"
        await ctx.send(f"I have toggled the Reaction Role for this guild. It is now {is_enabled}")

    @reactionroles.command(name = "add", aliases = ['mk', 'make'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    @is_setup()
    async def rr_add(self, ctx, emoji : typing.Union[discord.Embed, str], *, role : discord.Role = None):
        """Adds a new Reaction Role."""
        reacts = await self.get_current_reactions(ctx.guild.id)

        if len(reacts) >= 20:
            await ctx.send(f"This bot currently does not support more than 20 reactions!")
            return
        
        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()

        elif isinstance(emoji, discord.Emoji):
            if not emoji.is_useable():
                await ctx.send("I cannot use that Emoji! Try again!")
                return

        try:
            tryrole = ctx.guild.get_role(role.id)
            try:
                await ctx.author.add_roles(tryrole, reason = "Reaction Role Setup Test #1")
            except:
                await ctx.author.remove_roles(tryrole, reason = "Reaction Role Setup Test #1")
                await ctx.author.add_roles(tryrole, reason = "Added back the role for the Reaction Role Setup Test #1!")
        except:
            await ctx.send('I am missing some permissons for adding and/or removing the role! Please fix this then Try again later!')
            return

        emoji = str(emoji)
        await self.bot.reaction_roles.upsert(
            {
                "_id": emoji,
                "role": role.id,
                "guild_id": ctx.guild.id
            }
        )

        await self.rebuild_role_embed(ctx.guild.id)

        await ctx.send("The Reaction Role is ready and good to go!")

    @reactionroles.command(name = "remove", aliases = ['rm'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_roles = True)
    @is_setup()
    async def rr_remove(self, ctx, emoji : typing.Union[discord.Emoji, str]):
        """Remove an existing Reaction Role using it's emoji!"""

        if not isinstance(emoji, discord.Emoji):
            emoji = emojis.get(emoji)
            emoji = emoji.pop()

        emoji = str(emoji)
        try:
            await self.bot.reaction_roles.delete(emoji)
        except:
            await ctx.send(f'{emoji} is not a valid Reaction Role Emoji!')
            return

        await self.rebuild_role_embed(ctx.guild.id)

        await ctx.send("That should be all done and Removed!")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))

        role = guild.get_role(emoji_data["role"])

        member = await guild.fetch_member(payload.user_id)

        if member.bot:
            return

        if role not in member.roles:
            await member.add_roles(role, reason = f'Reaction Roles!')

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        data = await self.bot.config.find(payload.guild_id)

        if not payload.guild_id or not data or not data.get("is_enabled"):
            return

        guild_reaction_roles = await self.get_current_reactions(payload.guild_id)
        if str(payload.emoji) not in guild_reaction_roles:
            return

        guild = await self.bot.fetch_guild(payload.guild_id)

        emoji_data = await self.bot.reaction_roles.find(str(payload.emoji))

        role = guild.get_role(emoji_data["role"])

        member = await guild.fetch_member(payload.user_id)

        if role in member.roles:
            await member.remove_roles(role, reason = f'Reaction Roles!')

    @reactionroles.command(name = "set")
    @commands.guild_only()
    @commands.has_guild_permissions(administrator = True)
    @is_setup()
    async def rr_set(self, ctx, types = None, *, message = None): #Description, Title, Color
        """Sets a specific item of the Reaction Role Embed."""
        with open('BotRecords/reaction.json', 'r') as f:
            reaction = json.load(f)

        data = await self.bot.config.find(ctx.guild.id)

        channel_id = data['channel_id']
        message_id = data['message_id']
        guild_id = ctx.guild.id

        channel = await self.bot.fetch_channel(channel_id)
        message = await channel.fetch_message(message_id)

        if types == None:
            await ctx.send('Please put a type! Like `Title`, `Description`, and `Color`!')
            return
        if message == None:
            await ctx.send('Please put a message for the Embed\'s {}!'.format(str(types)))

        finaltype = str(types).lower()

        if finaltype == "title":
            reaction[str(ctx.guild.id)]["title"] = str(message)

            embed = discord.Embed(
                title = str(reaction[str(guild_id)]["title"]),
                color = int(reaction[str(guild_id)]["color"]),
                description = str(reaction[str(guild_id)]["desc"])
            )
        if finaltype == "description":
            reaction[str(ctx.guild.id)]["desc"] = str(message)

            embed = discord.Embed(
                title = str(reaction[str(guild_id)]["title"]),
                color = int(reaction[str(guild_id)]["color"]),
                description = str(reaction[str(guild_id)]["desc"])
            )
        if finaltype == "desc":
            reaction[str(ctx.guild.id)]["desc"] = str(message)

            embed = discord.Embed(
                title = str(reaction[str(guild_id)]["title"]),
                color = int(reaction[str(guild_id)]["color"]),
                description = str(reaction[str(guild_id)]["desc"])
            )
        if finaltype == "color":
            if str(message).startswith("#"):
                str(message).replace("#", "0x")
                try:
                    message = int(message)
                except:
                    await ctx.send('It is not a HEX Code! Try again later!')
                    return

                reaction[str(ctx.guild.id)]["color"] = str(message)

                embed = discord.Embed(
                    title = str(reaction[str(guild_id)]["title"]),
                    color = int(reaction[str(guild_id)]["color"]),
                    description = str(reaction[str(guild_id)]["desc"])
                )
            else:
                await ctx.send('It is not a HEX Code! Try again later!')
                return

        await message.edit(embed=embed)

    @commands.command(aliases = ['react-to', 'reactto', 'react'])
    async def react_to(self, ctx, message : discord.Message = None, *, emoji: discord.Emoji = None):
        if message == None:
            await ctx.send(f"Please put the message ID for the bot to react. Usage: `lm?react <Channel ID (If None, Picks the current channel --> {ctx.channel.mention})>-<Message ID> <Emoji (Either the name or the emoji itself works)>`!")
            return

        try:
            channel = await self.bot.fetch_channel(message.channel.id)
            message = await channel.fetch_message(message.id)
        except:
            await ctx.send("Message Not Found!")

        if emoji == None:
            await ctx.send(f"Please put an emoji to be reacted to the message. Usage: `lm?react <Channel ID (If None, Picks the current channel --> {ctx.channel.mention})>-<Message ID> <Emoji (Either the name or the emoji itself works)>`!")
            return

        try:
            await message.add_reaction(emoji)
        except discord.HTTPException:
            await ctx.send(f"Emoji named `{str(emoji)}` Not Found!")
            return

        await ctx.send("Done! Reaction has been added!")


def setup(bot):
    bot.add_cog(Reactions(bot))
    print('Reactions Cog Is Ready!')