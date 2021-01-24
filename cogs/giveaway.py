import discord
from discord.ext import commands
from discord.ext import flags
import asyncio
import random
import datetime
import os
import json
from typing import Union
import emojis

os.chdir("/home/gilb/LyricMaster/")

def convert(time):
    pos = ['s', 'm', 'h', 'd']

    time_dict = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 3600*24
    }
    
    unit = time[-1]

    if unit not in pos:
        return -1
    try:
        val = int(time[:-1])
    except:
        return -2

    return val * time_dict[unit]

class UnicodeEmojiNotFound(commands.BadArgument):
    def __init__(self, argument):
        self.argument = argument
        super().__init__(f'Unicode emoji "{argument}" not found.')

class UnicodeEmojiConverter(commands.Converter):
    async def convert(self, ctx, argument):
        if not (emoji := emojis.db.get_emoji_by_code(argument)):
            raise UnicodeEmojiNotFound(argument)

        return emoji.emoji

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(aliases = ['g', 'gw'])
    @commands.guild_only()
    async def giveaway(self, ctx):
        if ctx.invoked_subcommand is None:
            self.bot.get_command('help giveaway')

    @flags.add_flag("--time", type=str, default=None)
    @flags.add_flag("--prize", type=str, default=None)
    @flags.add_flag("--channel", type=discord.TextChannel, default=None)
    @flags.add_flag("--host", type=discord.Member, default=None)
    #@flags.add_flag("--emoji", type=Union[discord.Emoji, discord.PartialEmoji, UnicodeEmojiConverter], default="🎉")
    @flags.add_flag("--ping", type=discord.Role, default=None)
    #@flags.add_flag("--color", type=str, default=None)
    @giveaway.command(cls=flags.FlagCommand)
    @commands.has_guild_permissions(manage_guild=True)
    async def start(self, ctx, **flags):
        print(flags)
        timeFlag = flags[
            "time"
        ]
        prizeFlag = flags[
            "prize"
        ]
        channelFlag = flags[
            "channel"
        ]
        hostFlag = flags[
            "host"
        ]
        #emojiFlag = flags[
        #    "emoji"
        #]
        pingFlag = flags[
            "ping"
        ]
        #colorFlag = flags[
        #    "color"
        #]

        if timeFlag == None:
            await ctx.send(
                "Missing required argument, `time`. Usage: `lm?g start --time <Time (5s, 10h, 1d, 2w)> --channel {} --prize <Prize Name Here>".format(
                    ctx.channel.mention
                )
            )
            return
        if prizeFlag == None:
            await ctx.send(
                "Missing required argument, `prize`. Usage: `lm?g start --time <Time (5s, 10h, 1d, 2w)> --channel {} --prize <Prize Name Here>".format(
                    ctx.channel.mention
                )
            )
            return
        if channelFlag == None:
            await ctx.send(
                "Missing required argument, `channel`. Usage: `lm?g start --time <Time (5s, 10h, 1d, 2w)> --channel {} --prize <Prize Name Here>".format(
                    ctx.channel.mention
                )
            )
            return

        #if colorFlag == None:
        #    colorFlag = ctx.author.color
        #    
        #if str(colorFlag).endswith(
        #    (
        #        "#", "0x"
        #    )
        #):
        #    ColorFlag = str(
        #        colorFlag
        #    ).replace(
        #        "#", "0x"
        #    )
        #    try:
        #        finalColor = int(
        #            ColorFlag
        #        )
        #    except:
        #        await ctx.send(
        #            "{} is not a HEX Code!".format(
        #                str(
        #                    colorFlag
        #                )
        #            )
        #        )
        #        return
        
        channel = ctx.guild.get_channel(
            int(
                channelFlag.id
            )
        )

        time = convert(
            str(
                timeFlag
            )
        )

        if time == -1:
            await ctx.send(f"You didn't answer the time with a proper unit. Use (s|m|h|d) next time!")
            return
        elif time == -2:
            await ctx.send(f"The time must be an integer. Please enter an integer next time")
            return

        prize = str(
            prizeFlag
        )

        await ctx.send(
            "The giveaway will be in {} and will last {} with the prize {}!".format(
                channel.mention, 
                timeFlag, 
                prize
            )
        )

        finalColor = discord.Color.random()

        embed = discord.Embed(
            title = "New Giveaway!", 
            description = "Prize: {prize!r}".format(
                **flags
            ).replace(
                "'", '"'
            ), 
            color = finalColor
        )
        embed.add_field(
            name = "Hosted by:",
            value = f"{str(hostFlag.name)}#{str(hostFlag.discriminator)}" if hostFlag != None else f'{str(ctx.author.name)}#{str(ctx.author.discriminator)}',
            inline = False
        )
        embed.set_footer(text = "STATUS: Ongoing | Ends {} from now!".format(timeFlag))

        if pingFlag != None:
            await ctx.send("{}".format(pingFlag.mention))
        else:
            pass

        msg = await ctx.send(embed=embed)

        await msg.add_reaction(f"🎉")

        with open("BotRecords/giveaway.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)][str(channel.id)] = {}
        data[str(ctx.guild.id)][str(channel.id)][str(msg.id)] = {}
        data[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Status"] = "Ongoing"
        if hostFlag != None:
            data[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Host"] = f"{str(hostFlag.name)}#{str(hostFlag.discriminator)}"
        else:
            data[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Host"] = f'{str(ctx.author.name)}#{str(ctx.author.discriminator)}'
        data[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Color"] = str(finalColor)
        data[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Prize"] = str(prize)

        with open("BotRecords/giveaway.json", "w") as f:
            json.dump(data, f, indent=4)

        await asyncio.sleep(time)

        with open("BotRecords/giveaway.json", "r") as f:
            datas = json.load(f)

        if datas[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Status"] != "Ongoing":
            return
        else:
            pass

        new_msg = await channel.fetch_message(msg.id)

        users = await new_msg.reactions[0].users().flatten()
        users.pop(users.index(self.bot.user))

        winner = random.choice(users)

        em = discord.Embed(
            title = "Giveaway ENDED!",
            description = "Prize: {prize!r}".format(**flags), 
            color = finalColor
        )
        em.add_field(
            name = "Hosted by:",
            value = datas[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Host"],
            inline = False
        )
        em.add_field(
            name = "Winner:",
            value = winner.mention,
            inline = False
        )
        em.set_footer(text = "STATUS: Ended!")

        await new_msg.edit(embed=em)

        await channel.send(f"Congratulations! {winner.mention} won {prize}!")

        with open("BotRecords/giveaway.json", "r") as f:
            enddata = json.load(f)

        enddata[str(ctx.guild.id)][str(channel.id)][str(msg.id)]["Status"] = "Ended"

        with open("BotRecords/giveaway.json", "w") as f:
            json.dump(enddata, f, indent=4)

    @flags.add_flag("--channel", type=discord.TextChannel, default = None)
    @flags.add_flag("--id", type=str, default = None)
    @giveaway.command(cls=flags.FlagCommand)
    @commands.has_guild_permissions(manage_guild=True)
    async def reroll(self, ctx, **flags):
        channelFlag = flags["channel"]
        idFlag = flags["id"]

        if channelFlag == None:
            await ctx.send(f"Missing required argument, `channel`. Usage: `lm?giveaway reroll --channel <Channel (e.g {ctx.channel.mention})> --id <Message ID of the Giveaway>`!")
            return
        if idFlag == None:
            await ctx.send(f"Missing required argument, `id`. Usage: `lm?giveaway reroll --channel <Channel (e.g {ctx.channel.mention})> --id <Message ID of the Giveaway>`!")
            return

        try:
            int(idFlag)
        except:
            await ctx.send("The ID was entered incorrectly!")
            return

        try:
            with open("BotRecords/giveaway.json", "r") as f:
                data = json.load(f)

            if str(channelFlag.id) not in data[str(ctx.guild.id)]:
                await ctx.send("Giveaway Not Found!")
                return
            if str(idFlag) not in data[str(ctx.guild.id)][str(channelFlag.id)]:
                await ctx.send("Giveaway Not Found!")
                return

            if data[str(ctx.guild.id)][str(channelFlag.id)][str(idFlag)]["Status"] == "Ongoing":
                await ctx.send("That giveaway is still Ongoing!")
                return

            get_msg_id = str(data[str(ctx.guild.id)][channelFlag.id][str(idFlag)])

            msg = await channelFlag.fetch_message(int(get_msg_id))

            users = await msg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))

            winner = random.choice(users)

            await channelFlag.send(f"Rerolled Giveaway: Congratulations! Thhe new winner is {winner.mention}!")

            data[str(ctx.guild.id)][str(channelFlag.id)][str(idFlag)]["Status"] = "Ended"

            with open("BotRecords/giveaway.json", "w") as f:
                json.dump(data, f, indent=4)
        except:
            await ctx.send("Giveaway Not Found!")

    @flags.add_flag("--channel", type=discord.TextChannel, default = None)
    @flags.add_flag("--id", type=str, default = None)
    @giveaway.command(cls=flags.FlagCommand)
    @commands.has_guild_permissions(manage_guild=True)
    async def end(self, ctx, **flags):
        channelFlag = flags["channel"]
        idFlag = flags["id"]

        if channelFlag == None:
            await ctx.send(f"Missing required argument, `channel`. Usage: `lm?giveaway end --channel <Channel (e.g {ctx.channel.mention})> --id <Message ID of the Giveaway>`!")
            return
        if idFlag == None:
            await ctx.send(f"Missing required argument, `id`. Usage: `lm?giveaway end --channel <Channel (e.g {ctx.channel.mention})> --id <Message ID of the Giveaway>`!")
            return

        try:
            int(idFlag)
        except:
            await ctx.send("The ID was entered incorrectly!")
            return

        try:
            with open("BotRecords/giveaway.json", "r") as f:
                data = json.load(f)

            if str(channelFlag.id) not in data[str(ctx.guild.id)]:
                await ctx.send("Giveaway Not Found!")
                return
            if str(idFlag) not in data[str(ctx.guild.id)][str(channelFlag.id)]:
                await ctx.send("Giveaway Not Found!")
                return

            if data[str(ctx.guild.id)][str(channelFlag.id)][str(idFlag)]["Status"] == "Ended":
                await ctx.send("That giveaway is Already Ended!")
                return

            get_msg_id = str(data[str(ctx.guild.id)][channelFlag.id][str(idFlag)])

            msg = await channelFlag.fetch_message(int(get_msg_id))

            users = await msg.reactions[0].users().flatten()
            users.pop(users.index(self.bot.user))

            winner = random.choice(users)
            prize = data[str(ctx.guild.id)][str(channelFlag.id)][str(idFlag)]["Prize"]

            em = discord.Embed(
                title = "Giveaway ENDED!",
                description = "Prize: {prize!r}".format(**flags), 
                color = int(data[str(ctx.guild.id)][str(channelFlag.id)][str(msg.id)]["Color"])
            )
            em.add_field(
                name = "Hosted by:",
                value = data[str(ctx.guild.id)][str(channelFlag.id)][str(msg.id)]["Host"],
                inline = False
            )
            em.add_field(
                name = "Winner:",
                value = winner.mention,
                inline = False
            )
            em.set_footer(text = "STATUS: Ended!")

            await msg.edit(embed=em)

            await channelFlag.send(f"Congratulations! {winner.mention} won {prize}!")

            data[str(ctx.guild.id)][str(channelFlag.id)][str(msg.id)]["Status"] = "Ended"

            with open("BotRecords/giveaway.json", "w") as f:
                json.dump(data, f, indent=4)
        except:
            await ctx.send("Giveaway Not Found!")

def setup(bot):
    bot.add_cog(Giveaway(bot))
    print("Giveaway Cog Is Ready!")