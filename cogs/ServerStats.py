#-------------IMPORTS-------------#
import discord
from discord.ext import commands
import asyncio
import os
import json
import typing
from typing import Union

#-------------DIRECTORY CHANGE-------------#
os.chdir("/home/gilb/LyricMaster/BotRecords/")

#-------------CLASS-------------#
class Server_Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

#-------------EVENTS-------------#

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("serverstats.json", "r") as f:
            data = json.load(f)

        if str(member.guild.id) not in data:
            return
        if data[str(member.guild.id)]["Status"] == False:
            return

        id_bot = str(data[str(member.guild.id)]["BotChannel"])
        id_human = str(data[str(member.guild.id)]["HumanChannel"])
        id_glob = str(data[str(member.guild.id)]["Global"])

        botchannel = member.guild.get_channel(int(id_bot["ID"]))
        globalchannel = member.guild.get_channel(int(id_glob["ID"]))
        humanchannel = member.guild.get_channel(int(id_human["ID"]))

        bot = 0
        nonbot = 0

        for mems in member.guild.members:
            if mems.bot:
                bot += 1
            else:
                nonbot += 1

            glob = round(bot + nonbot)

        bot_count = str(bot)
        human_count = str(nonbot)
        all_count = str(glob)
            
        await botchannel.edit(name = f"{str(id_bot['Name'])}")
        await globalchannel.edit(name = f"{str(id_glob['Name'])}")
        await humanchannel.edit(name = f"{str(id_human['Name'])}")

    @commands.Cog.listener()
    async def on_member_leave(self, member):
        with open("serverstats.json", "r") as f:
            data = json.load(f)

        if str(member.guild.id) not in data:
            return
        if data[str(member.guild.id)]["Status"] == False:
            return

        id_bot = str(data[str(member.guild.id)]["BotChannelID"])
        id_human = str(data[str(member.guild.id)]["HumanChannelID"])
        id_glob = str(data[str(member.guild.id)]["GlobalID"])

        botchannel = member.guild.get_channel(int(id_bot))
        globalchannel = member.guild.get_channel(int(id_glob))
        humanchannel = member.guild.get_channel(int(id_human))

        bot = 0
        nonbot = 0

        for mems in member.guild.members:
            if mems.bot:
                bot += 1
            else:
                nonbot += 1

            glob = round(bot + nonbot)

        bot_count = str(bot)
        human_count = str(nonbot)
        all_count = str(glob)
            
        await botchannel.edit(name = f"Bots: {str(bot)}")
        await globalchannel.edit(name = f"Members: {str(human_count)}")
        await humanchannel.edit(name = f"Humans: {str(all_count)}")

#-------------COMMANDS-------------#
    
    @commands.group(aliases = ['server_stats', 'server-stats', 'guildstats', 'guild-stats', 'guild_stats', 'ss', 'gs', 's-s', 'g_s', 'g-s', 's_s'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def serverstats(self, ctx):
        if ctx.invoked_subcommand is None:
            try:
                self.bot.get_command("help serverstats")
            except:
                await ctx.send("Something wen't wrong. Try again in a few moments.")
                return

    @serverstats.command(name = 'rename', aliases = ['--rename', '-rename'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def ss_rename(self, ctx, channel : Union[discord.TextChannel, discord.VoiceChannel], *, name = None):
        if type == None:
            config = discord.Embed()
            config.title = "Renaming Voice Channels For Server Stats:"
            config.color = discord.Color.blue if ctx.author.color == 0 else ctx.author.color
            config.description = """
e.g ```
lm?serverstats --rename <Name>
```

Config Variables:
[bot_count] = Count for bots
[human_count] = Count for humans
[all_count] = All people (Including bot and human) count
            """.replace("[", "{").replace("]", "}")
            return await ctx.send(embed=config)

        #if 

    @serverstats.command(name = 'toggle', aliases = ['--toggle', '-toggle'])
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def ss_toggle(self, ctx):
        with open("serverstats.json", "r") as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            data[str(ctx.guild.id)] = {}
            data[str(ctx.guild.id)]["Status"] = True
        else:
            data[str(ctx.guild.id)]["Status"] = not data[str(ctx.guild.id)]["Status"]

        with open("serverstats.json", "w") as f:
            json.dump(data, f, indent=4)

        is_enabled = "enabled!" if data[str(ctx.guild.id)]["Status"] else "disabled!"
        if is_enabled == "enabled!":
            if "Global" in data[str(ctx.guild.id)]:
                pass
            else:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                }
                bot = 0
                nonbot = 0

                for mems in ctx.guild.members:
                    if mems.bot:
                        bot += 1
                    else:
                        nonbot += 1

                    glob = round(bot + nonbot)

                globalChannel = await ctx.guild.create_text_channel(f'Members: {str(glob)}', overwrites=overwrites)

                with open("serverstats.json", "r") as fps:
                    datas = json.load(fps)

                datas[str(ctx.guild.id)] = {}
                datas[str(ctx.guild.id)]["Global"] = {}
                datas[str(ctx.guild.id)]["Global"]["ID"] = str(globalChannel.id)
                datas[str(ctx.guild.id)]["Global"]["Name"] = "Members: [human_count]".replace("[", "{").replace("]", "}")

                with open("serverstats.json", "w") as f:
                    json.dump(datas, f, indent=4)

            if "HumanChannelID" in data[str(ctx.guild.id)]:
                pass
            else:
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                }
                nonbot = 0

                for mems in ctx.guild.members:
                    if mems.bot:
                        pass
                    else:
                        nonbot += 1

                humanChannel = await ctx.guild.create_text_channel(f'Humans: {str(nonbot)}', overwrites=overwrites)

                with open("serverstats.json", "r") as fps:
                    datas = json.load(fps)

                datas[str(ctx.guild.id)] = {}
                datas[str(ctx.guild.id)]["HumanChannel"] = {}
                datas[str(ctx.guild.id)]["HumanChannel"]["ID"] = str(humanChannel.id)
                datas[str(ctx.guild.id)]["HumanChannel"]["Name"] = "Humans: [all_count]".replace("[", "{").replace("]", "}")

                with open("serverstats.json", "w") as f:
                    json.dump(datas, f, indent=4)

            if "BotChannelID" in data[str(ctx.guild.id)]:
                pass
            else:
                #bot_count = str(bot)
                #human_count = str(nonbot)
                #all_count = str(glob)
                overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(read_messages = False),
                }
                nonbot = 0

                for mems in ctx.guild.members:
                    if mems.bot:
                        pass
                    else:
                        nonbot += 1

                humanChannel = await ctx.guild.create_text_channel(f'Humans: {str(nonbot)}', overwrites=overwrites)

                with open("serverstats.json", "r") as fps:
                    datas = json.load(fps)

                datas[str(ctx.guild.id)] = {}
                datas[str(ctx.guild.id)]["HumanChannel"] = {}
                datas[str(ctx.guild.id)]["HumanChannel"]["ID"] = str(humanChannel.id)
                datas[str(ctx.guild.id)]["HumanChannel"]["Name"] = "Humans: [all_count]".replace("[", "{").replace("]", "}")

                with open("serverstats.json", "w") as f:
                    json.dump(datas, f, indent=4)

        await ctx.send(f"I have toggled the Server Stats Function for this guild. It is now {is_enabled}.")

#-------------SETUP COG-------------#
def setup(bot):
    bot.add_cog(Server_Stats(bot))