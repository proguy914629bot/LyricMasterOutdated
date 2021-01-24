from captcha.image import ImageCaptcha
import random
from random import randrange
import os
import discord
from discord.ext import commands
from discord import Embed
import json
import asyncio
import requests

os.chdir("/home/gilb/LyricMaster/")

class Security(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        with open("BotRecords/captcha.json", "r") as f:
            datas = json.load(f)

        if member.guild.id not in datas:
            return

        r = requests.get(f"https://altdentifier.com/api/v2/user/{str(member.id)}/trustfactor")

        if r.status_code == 200:
            l_response = json.loads(r.content)
            try:
                trustfactor = l_response["trustfactor"]

                if trustfactor == 0:
                    with open("BotRecords/captcha.json", "r") as f:
                        jsondata = json.load(f)

                    image = ImageCaptcha(fonts = ["Others/font1.ttf", "Others/font2.ttf"])

                    num = randrange(1000, 9999)

                    data = image.generate(str(num))

                    image.write(str(num), 'Captcha.png')

                    memberrole = member.guild.get_role(int(jsondata[str(member.guild.id)]["Role"]))
                    if memberrole in member.roles:
                        return

                    files = discord.File("Captcha.png")
                    embed = Embed(
                        title = "Captcha Verification: ",
                        description = f'''
Seems like you are an Alt Account. To get the role {memberrole.mention} in {member.guild.name}, You must pass this Capthca verification test first!!
                        ''',
                        color = member.color,
                    )
                    embed.set_image(
                        url = "attachment://captcha.png"
                    )
                    embed.set_footer(
                        text = "Powered by AltDentifier",
                        icon_url = "https://avatars1.githubusercontent.com/u/36313629?s=280&v=4"
                    )
                    await asyncio.sleep(7)

                    try:
                        await member.send(embed=embed, file=files)
                    except:
                        return

                    answers = []

                    def check(m):
                        return m.author == member and member.guild is None
                    if memberrole in member.roles:
                        return

                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                    except asyncio.TimeoutError:
                        if memberrole in member.roles:
                            return
                        await member.send("Took To Long. Kicking you out!")
                        await member.kick(reason = f"Took to long to do an easy Captcha Verification!")
                    else:
                        answers.append(msg.content)

                    if memberrole in member.roles:
                        return

                    if answers[0] == str(num):
                        if memberrole in member.roles:
                            return
                        
                        member.add_roles(memberrole)

                        if memberrole in member.roles:
                            return

                        await member.send("You have been Verified!")
                        return
                    else:
                        if memberrole in member.roles:
                            return

                        await member.send("Sorry! You got the wrong answer! I need to kick you now! Goodbye!")
                        await member.kick(reason = f"Captcha Answer Wrong! Supposed to be \"{num}\" but User answered \"{answers[0]}\"!")
                    return
                elif trustfactor == 1:
                    with open("BotRecords/captcha.json", "r") as f:
                        jsondata = json.load(f)

                    image = ImageCaptcha(fonts = ["Others/font1.ttf", "Others/font2.ttf"])

                    num = randrange(1000, 9999)

                    data = image.generate(str(num))

                    image.write(str(num), 'Captcha.png')

                    memberrole = member.guild.get_role(int(jsondata[str(member.guild.id)]["Role"]))
                    if memberrole in member.roles:
                        return

                    embed = Embed(
                        title = "Captcha Verification: ",
                        description = f'''
Seems Like you are an Alt Account. To get the role {memberrole.mention} in {member.guild.name}, You must pass this Capthca verification test first!
                        ''',
                        color = member.color,
                    )
                    files = discord.File("Captcha.png")
                    embed.set_image(
                        url = "attachment://Captcha.png"
                    )
                    embed.set_footer(
                        text = "Powered by AltDentifier",
                        icon_url = "https://avatars1.githubusercontent.com/u/36313629?s=280&v=4"
                    )
                    await asyncio.sleep(7)

                    try:
                        await member.send(embed=embed, file=files)
                    except:
                        return

                    answers = []

                    def check(m):
                        return m.author == member and member.guild is None
                    if memberrole in member.roles:
                        return

                    try:
                        msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                    except asyncio.TimeoutError:
                        if memberrole in member.roles:
                            return
                        await member.send("Took To Long. Kicking you out!")
                        await member.kick(reason = f"Took to long to do an easy Captcha Verification!")
                    else:
                        answers.append(msg.content)

                    if memberrole in member.roles:
                        return

                    if answers[0] == str(num):
                        if memberrole in member.roles:
                            return
                        
                        member.add_roles(memberrole)

                        if memberrole in member.roles:
                            return

                        await member.send("You have been Verified!")
                        return
                    else:
                        if memberrole in member.roles:
                            return

                        await member.send("Sorry! You got the wrong answer! I need to kick you now! Goodbye!")
                        await member.kick(reason = f"Captcha Answer Wrong! Supposed to be \"{num}\" but User answered \"{answers[0]}\"!")
                    return
                elif trustfactor >= 2:
                    with open("BotRecords/captcha.json", "r") as f:
                        jsondata = json.load(f)
                    
                    memberrole = member.guild.get_role(int(jsondata[str(member.guild.id)]["Role"]))
                    member.add_roles(memberrole, reason = f"Trusted from AltDentifier's API")

                    return
                return
            except:
                with open("BotRecords/captcha.json", "r") as f:
                    jsondata = json.load(f)

                image = ImageCaptcha(fonts = ["Others/font1.ttf", "Others/font2.ttf"])

                num = randrange(1000, 9999)

                data = image.generate(str(num))

                image.write(str(num), 'Captcha.png')

                memberrole = member.guild.get_role(int(jsondata[str(member.guild.id)]["Role"]))
                if memberrole in member.roles:
                    return

                embed = Embed(
                    title = "Captcha Verification: ",
                    description = f'''
To get the role {memberrole.mention} in {member.guild.name}, You must pass this Capthca verification test first!
                    ''',
                    color = member.color,
                )
                files = discord.File("Captcha.png")
                embed.set_image(
                    url = "attachment://Captcha.png"
                )
                embed.set_footer(
                    text = "Powered by AltDentifier",
                    icon_url = "https://avatars1.githubusercontent.com/u/36313629?s=280&v=4"
                )
                await asyncio.sleep(7)

                try:
                    await member.send(embed=embed, file=files)
                except:
                    return

                answers = []

                def check(m):
                    return m.author == member and member.guild is None
                if memberrole in member.roles:
                    return

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    if memberrole in member.roles:
                        return
                    await member.send("Took To Long. Kicking you out!")
                    await member.kick(reason = f"Took to long to do an easy Captcha Verification!")
                else:
                    answers.append(msg.content)

                if memberrole in member.roles:
                    return

                if answers[0] == str(num):
                    if memberrole in member.roles:
                        return
                    
                    member.add_roles(memberrole)

                    if memberrole in member.roles:
                        return

                    await member.send("You have been Verified!")
                    return
                else:
                    if memberrole in member.roles:
                        return

                    await member.send("Sorry! You got the wrong answer! I need to kick you now! Goodbye!")
                    await member.kick(reason = f"Captcha Answer Wrong! Supposed to be \"{num}\" but User answered \"{answers[0]}\"!")
                return

    @commands.group()
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def captcha(self, ctx):
        embed = discord.Embed(
            title = "Captcha Commands",
            color = ctx.author.color,
            timestamp = ctx.message.created_at
        )
        #embed.add_field(
        #    name = "Configure Command",
        #    value = f"```\nlm?captcha --configure\n```"
        #)

        embed.add_field(
            name = "Toggle Command:",
            value = f"```\nlm?captcha --toggle\n```\n\n",
            inline=False
        )
        embed.add_field(
            name = "Example Command:",
            value = f"```\nlm?captcha --example\n```\n\n",
            inline=False
        )
        await ctx.send(embed=embed)

    @captcha.command(aliases = ['--bypass', '-bypass', 'bypass'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def captcha_bypass(self, ctx, member: discord.Member):
        with open("BotRecords/captcha.json", "r") as f:
            data = json.load(f)

        if ctx.guild.id not in data:
            await ctx.send("You have not enabled Captcha yet!")
            return

        return

    @captcha.command(aliases = ['--example', '-example', 'example'])
    @commands.guild_only()
    async def captcha_example(self, ctx):
        image = ImageCaptcha(fonts=['Others/font1.ttf', 'Others/font2.ttf'])

        data = image.generate("1234")

        image.write("1234", 'CaptchaExample.png')

        embed = discord.Embed(
            title = "Example of an Captcha",
            color = ctx.author.color,
            timestamp = ctx.message.created_at
        )
        files = discord.File("CaptchaExample.png")
        embed.set_image(
            url = "attachment://CaptchaExample.png"
        )
        embed.set_footer(
            text = "Note that Captchas are generated with different numbers and characters. This is only an example of a single captcha with the answer \"1234\"!"
        )
        await ctx.send(embed=embed, file=files)

    @captcha.command(aliases = ['--configure', '-configure', 'configure'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def captcha_configure(self, ctx, args, *, args2):
        pass

    @captcha.command(aliases = ['--toggle', '-toggle', 'toggle'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def captcha_toggle(self, ctx):
        with open("BotRecords/captcha.json", "r") as f:
            data = json.load(f)

        if str(ctx.guild.id) not in data:
            await ctx.send("By enabling Captcha Powered by AltDentifier, You Agree to AltDentifier's ToS (Found Here: https://altdentifier.com/tos) and Discord's ToS (Found Here: https://discord.com/terms)! Reply with `Y` or `N`.")

            def check(m):
                return m.author == ctx.author and m.channel == ctx.channel

            msg = await self.bot.wait_for('message', check=check)

            cont = str(msg.content).lower()

            if cont == "y":
                await ctx.send("I have enabled Captcha for you!")

                data[str(ctx.guild.id)] = True

                with open("BotRecords/captcha.json", "w") as f:
                    json.dump(data, f, indent=4)
                return
            else:
                await ctx.send("You Did not agree to the ToS. This conversation will be reported and will be sent to Discord for further notice!")
                return
            return

        data[str(ctx.guild.id)]["is_enabled"] = not data[str(ctx.guild.id)]["is_enabled"]

        with open("BotRecords/captcha.json", "r") as f:
            json.dump(data, f, indent=4)

        is_enabled = "enabled" if data["is_enabled"] else "disabled"

        await ctx.send(f"Okay! I have toggled Captcha Verification. It is now {str(is_enabled).title()}!")

def setup(bot):
    bot.add_cog(Security(bot))
    print("Security Cog Is Ready!")