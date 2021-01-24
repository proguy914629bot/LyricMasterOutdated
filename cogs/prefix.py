import discord
from discord.ext import commands
import json
import asyncio

class Prefixes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def prefix(self, ctx, *, prefix = None):
        """Changes the prefix or views your prefixes!"""
        with open('ImportantFiles/guildprefix.json', 'r') as f:
            guildprefix = json.load(f)

        with open('ImportantFiles/memberprefix.json', 'r') as files:
            memberprefix = json.load(files)
        if prefix != None:
            checkprefix = str(prefix).replace(" ", "")
            if checkprefix == "<@755291533632077834>":
                await ctx.send("That is already a valid global prefix!")
                return
            if checkprefix == "<@!755291533632077834>":
                await ctx.send("That is already a valid global prefix!")
                return
            if checkprefix == "lm!":
                await ctx.send("That is already a valid global prefix!")
                return
            if checkprefix == "!lm":
                await ctx.send("That is already a valid global prefix!")
                return
            if checkprefix == "lm?":
                await ctx.send("That is already a valid global prefix!")
                return
            if checkprefix == "?lm":
                await ctx.send("That is already a valid global prefix!")
                return
            if str(ctx.guild.id) in guildprefix:
                if prefix == str(guildprefix[str(ctx.guild.id)]):
                    await ctx.send("That is already a valid guild prefix!")
                    return
            if str(ctx.author.id) in memberprefix:
                if prefix == str(memberprefix[str(ctx.author.id)]):
                    await ctx.send("That is already a valid member prefix!")
                    return
            
            if ctx.author.guild_permissions.administrator:
                await ctx.send("Since you are a administrator, You can either pick to change the original prefix to {} to the guild or yourself!\nOptions: \n- `guild` \n-`server` \n-`user` \n-`member`".format(prefix))

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel
                
                answers = []

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                except asyncio.TimeoutError:
                    await ctx.send("Took to long. Try again later.")
                    return
                else:
                    answers.append(msg.content)

                answer = str(answers[0]).lower()

                if answer == "guild":
                    if str(ctx.guild.id) in guildprefix:
                        originalguildprefix = guildprefix[str(ctx.guild.id)]
                    else:
                        originalguildprefix = None

                    guildprefix[str(ctx.guild.id)] = str(prefix)

                    with open("ImportantFiles/guildprefix.json", "w") as f:
                        json.dump(guildprefix, f, indent=4)

                    if originalguildprefix == None:
                        await ctx.send("This guild prefix has been changed into `{}`!".format(prefix))
                    else:
                        await ctx.send("This guild prefix has been changed from `{}` to `{}`!".format(str(originalguildprefix), str(prefix)))
                elif answer == "server":
                    if str(ctx.guild.id) in guildprefix:
                        originalserverprefix = guildprefix[str(ctx.guild.id)]
                    else:
                        originalserverprefix = None

                    guildprefix[str(ctx.guild.id)] = str(prefix)

                    with open("ImportantFiles/guildprefix.json", "w") as f:
                        json.dump(guildprefix, f, indent=4)

                    if originalserverprefix == None:
                        await ctx.send("This guild prefix has been changed into `{}`!".format(prefix))
                    else:
                        await ctx.send("This guild prefix has been changed from `{}` to `{}`!".format(str(originalserverprefix), str(prefix)))
                elif answer == "member":
                    if str(ctx.guild.id) in memberprefix:
                        originalmemberprefix = guildprefix[str(ctx.guild.id)]
                    else:
                        originalmemberprefix = None

                    memberprefix[str(ctx.author.id)] = str(prefix)

                    with open("ImportantFiles/memberprefix.json", "w") as f:
                        json.dump(memberprefix, f, indent=4)

                    if originalmemberprefix == None:
                        await ctx.send("This guild prefix has been changed into `{}`!".format(prefix))
                    else:
                        await ctx.send("This guild prefix has been changed from `{}` to `{}`!".format(str(originalmemberprefix), str(prefix)))
                elif answer == "user":
                    if str(ctx.guild.id) in memberprefix:
                        originaluserprefix = guildprefix[str(ctx.guild.id)]
                    else:
                        originaluserprefix = None

                    memberprefix[str(ctx.author.id)] = str(prefix)

                    with open("ImportantFiles/memberprefix.json", "w") as f:
                        json.dump(memberprefix, f, indent=4)

                    if originaluserprefix == None:
                        await ctx.send("This guild prefix has been changed into `{}`!".format(prefix))
                    else:
                        await ctx.send("This guild prefix has been changed from `{}` to `{}`!".format(str(originaluserprefix), str(prefix)))
                else:
                    await ctx.send("We do not support {} as an answer! Try again!".format(str(answers[0])))
                return
        else:
            embed = discord.Embed(
                title = f'Prefixes: ',
                color = ctx.author.color,
                description = f'Here are the prefixes for globally, this server (`{ctx.guild.name}`) and for your personal\nConfigure these at anytime by doing the `lm?prefix <prefix>` command!'
            )
            embed.add_field(
                name = 'Global Prefixes: (Prefixes that applies to all server that the bot is in)',
                value = '- <@!755291533632077834>\n- lm!\n- !lm\n- lm?\n- ?lm'
            )
            guildid = str(ctx.guild.id)
            memberid = str(ctx.author.id)
            if str(ctx.guild.id) in guildprefix:
                serverprefix = str(guildprefix[guildid])
                embed.add_field(
                    name = 'Guild Prefixes: (Prefixes that only applies to this guild)',
                    value = str(serverprefix)
                )
            else:
                pass

            if str(ctx.author.id) in memberprefix:
                membersprefix = str(memberprefix[memberid])
                embed.add_field(
                    name = 'Member Prefixes: (Prefixes that only applies to you in any server)',
                    value = str(membersprefix)
                )
            else:
                pass

            await ctx.send(embed=embed)
            return

def setup(bot):
    bot.add_cog(Prefixes(bot))
    print('Custom Prefix Cog Is Ready!')