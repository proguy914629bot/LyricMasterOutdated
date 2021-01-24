import discord
from discord.ext import commands
from discord.ext import tasks
import fortnite_python
import pfaw
from pfaw import Fortnite as fort
from pfaw import Platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--no-sandbox')
driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)

class Fortnite(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fortnite(self, ctx, args = None, args2 = None, args3 = None):
        finalargs = str(args).lower()
        if finalargs == ("status", "server"):
            async with ctx.message.channel.typing():
                driver.get(f"https://status.epicgames.com/")

                FortniteStatus = driver.find_elements_by_class_name("component-status tool tooltipstered")[0].text
        if finalargs == "stats":
            if args2 == None:
                await ctx.send('Please put a Valid Username!')
                return
            if args3 == None:
                await ctx.send(f'''
Please specify a Platform!

Here are the available platforms:
```css
"PC",
"Laptop",
"Xbox",
"PS4"

More Platforms upcoming!
                ''')
            finalargs3 = str(args3).lower()
            if finalargs3 == ("pc", "laptop"):
                stats = fortnite.battle_royale_stats(username = str(args2), platform=Platform.pc)
            if finalargs3 == "xbox":
                stats = fortnite.battle_royale_stats(username = str(args2), platform=Platform.xb1)
            if finalargs3 == "ps4":
                stats = fortnite.battle_royale_stats(username = str(args2), platform=Platform.ps4)
            else:
                await ctx.send(f'Platform {str(finalargs).title()} is not supported!')
                return

            if stats == None:
                await ctx.send(f'Either We cannot find the Fortnite Username {str(args2)} or the platofrm that you specified which is {str(finalargs).title()} is not used by the user!')
                return

            player = fortnite.player(username = str(args2))

            embed = discord.Embed(
                title = f"Stats for {str(args2)}:",
                color = ctx.author.color
            )
            embed.add_field(
                name = "Player Name:",
                value = str(player.name),
                inline=False
            )
            embed.add_field(
                name = "Player ID:",
                value = str(player.id),
                inline=False
            )
            embed.add_field(
                name = "Solo Stats:",
                value = f'''
Wins: {str(stats.solo.wins)}
Top 25: {str(stats.solo.top25)}
Top 10: {str(stats.solo.top10)}
Top 5: {str(stats.solo.top5)}
Top 3: {str(stats.solo.top3)}
                ''',
                inline = False
            )
            embed.add_field(
                name = "Duo Stats:",
                value = f'''
Wins: {str(stats.duo.wins)}
Top 25: {str(stats.duo.top25)}
Top 10: {str(stats.duo.top10)}
Top 5: {str(stats.duo.top5)}
Top 3: {str(stats.duo.top3)}
                ''',
                inline = False
            )
            embed.add_field(
                name = "Squad Stats:",
                value = f'''
Wins: {str(stats.squad.wins)}
Top 25: {str(stats.squad.top25)}
Top 10: {str(stats.squad.top10)}
Top 5: {str(stats.squad.top5)}
Top 3: {str(stats.squad.top3)}
                ''',
                inline = False
            )
            embed.add_field(
                name = "Lifetime Stats:",
                value = f'''
Wins: {str(stats.all.wins)}
Top 25: {str(stats.all.top25)}
Top 10: {str(stats.all.top10)}
Top 5: {str(stats.all.top5)}
Top 3: {str(stats.all.top3)}
                ''',
                inline = False
            )

def setup(bot):
    bot.add_cog(Fortnite(bot))