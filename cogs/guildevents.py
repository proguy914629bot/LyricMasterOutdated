import discord
from discord.ext import commands

class GuildEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.lastChannelID = {}

    @commands.Cog.listener()
    async def on_guild_join(self, guild): #Make an announcement when the bot join and make the bot server deafen
        member = guild.get_member(755291533632077834)

        channel0 = guild.text_channels[0]

        channel = guild.text_channels

        #vcchannel = guild.voice_channels
        #try:
        #    await vcchannel[0].connect()
        #except:
        #    try:
        #        await vcchannel[1].connect()
        #    except:
        #        try:
        #            await vcchannel[2].connect()
        #        except:
        #            try:
        #                await vcchannel[3].connect()
        #            except:
        #                try:
        #                    await vcchannel[4].connect()
        #                except:
        #                    try:
        #                        await vcchannel[5].connect()
        #                    except:
        #                        pass

        #try:
        #    await member.edit(deafen = True)
        #except discord.HTTPException:
        #    pass

        embed = discord.Embed(
            title = f"<a:facing_right_arrow:799579865296535583> Thanks For Inviting LyricMaster! <a:facing_left_arrow:799579706688667669>",
            description = f"{str(self.bot.description)}\nI am A Music Bot, You can get quick lyrics from me too. I also have Economy Commands and Bot-Related Commands.\nTo view these comamnds, Do the help command\n\nMy Prefixes: \n- `lm!` \n- `lm?` \n- `!lm` \n- `?lm` \n- When you mention him \n- Without the prefix e.g `help`.\n\nHope you enjoy the bot!\n\nRegards,\nLyricMaster#9688",
            color = 0x0fffff,
            url = "https://lyricmaster.ayomerdeka.com/"
        )
        embed.set_footer("Thanks for inviting LyricMaster!\nHope you enjoy the bot!", "https://cdn.discordapp.com/attachments/792327068398125077/794068939989712906/LyricMaster.jpg")
        embed.set_author("LyricMaster#9688", "https://lyricmaster.ayomerdeka.com", "https://cdn.discordapp.com/attachments/792327068398125077/794068939989712906/LyricMaster.jpg")

        try:
            await channel0.send(embed=embed)
        except: #Likely not gonna happen but just in case it does...
            try:
                await channel[1].send(embed=embed)
            except:
                try:
                    await channel[2].send(embed=embed)
                except:
                    try:
                        await channel[3].send(embed=embed)
                    except:
                        try:
                            await channel[4].send(embed=embed)
                        except:
                            try:
                                await channel[5].send(embed=embed)
                            except:
                                pass

        return

    @commands.Cog.listener()
    async def on_command_completion(self, ctx):
        self.bot.lastChannelID[str(ctx.guild.id)] = str(ctx.channel.id)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.id != 755291533632077834:
            return
        
        if after.deaf == False:
            await member.edit(deafen = True, reason = f"Deafened Myself.")
        else:
            return
        
        if str(member.guild.id) not in self.bot.lastChannelID:
            return

        channel = member.guild.get_channel(int(self.bot.lastChannelID[str(member.guild.id)]))

        msg = """
Please don't Undeafen me. I have deafened myself. Thanks!
        """

        embed = discord.Embed(description = msg)

        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        try:
            self.bot.lastChannelID.pop(str(guild.id))
        except KeyError:
            pass

def setup(bot):
    bot.add_cog(GuildEvents(bot))
    print("Guild Events Cog Is Ready!")