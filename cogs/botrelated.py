import discord
from discord.ext import commands
from pymongo import MongoClient
import typing
from discord.utils import get
import os
import inspect
import aiohttp
import psutil
from datetime import datetime
from aiohttp import ClientSession
from bs4 import BeautifulSoup
import urllib.request
from urllib.request import Request, urlopen
import re
from lxml import html
import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
import aiohttp
import asyncio
import functools
from bs4.element import NavigableString
import platform

async def check_url(url):
    try:
        async with aiohttp.ClientSession() as sessions:
            async with sessions.get(str(url)) as resp:
                resp.status == 200
                return [resp.status, True]
    except aiohttp.ClientError:
        return [404, False]

def typings(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        context = args[0] if isinstance(args[0], commands.Context) else args[1]
        async with context.typing():
            await func(*args, **kwargs)
    return wrapped

class Bot_Related(commands.Cog, name = "Bot"):
    """
    All Commands that are related to bots and LyricMaster's Bot Commands\n
    """
    def __init__(self, bot):
        self.bot = bot
        self.client = MongoClient()
        self.inviteLink = "https://lyricmaster.ayomerdeka.com/invite"
        self.domainLink = "https://lyricmaster.ayomerdeka.com/"

    def get_content(self, tag):
        """Returns content between two h2 tags"""

        bssiblings = tag.next_siblings
        siblings = []
        for elem in bssiblings:
            # get only tag elements, before the next h2
            # Putting away the comments, we know there's
            # at least one after it.
            if type(elem) == NavigableString:
                continue
            # It's a tag
            if elem.name == 'h2':
                break
            siblings.append(elem.text)
        content = '\n'.join(siblings)
        if len(content) >= 1024:
            content = content[:1021] + '...'

        return content

    @commands.command(aliases = ['owners', 'owner', 'credits'])
    async def credit(self, ctx):
        owner = self.bot.get_user(self.bot.owner_id)
        embed = discord.Embed()
        embed.title = f"Owner of this bot ({str(self.bot.user)}):"
        embed.set_thumbnail(url = f"{str(owner.avatar_url)}")
        embed.description = f"**Owner:**\nUsername: `{str(owner)}`\nID: `{str(owner.id)}`"
        embed.color = discord.Color.blue() if ctx.author.color.value == 0 else ctx.author.color

        await ctx.send(embed=embed)

    @commands.command(aliases = ['latency'])
    async def ping(self, ctx):
        f"""Get the latency/ping of the bot in the form of milliseconds.\nUsage: lm!ping"""
        embed = discord.Embed(
            title = 'Pings/Latencies: ',
            color = 0x2F3136,
            timestamp = ctx.message.created_at
        )
        embed.add_field(
            name = f"<a:typing:792292747695751179> Server & Typing/General Latency:",
            value = f"{round(self.bot.latency * 1000)}ms",
            inline=False
        )
        try:
            embed.add_field(
                name = f"<a:loading:792292697817743390> Websocket/VC Latency:",
                value = f'Avarage Latency: {round(int(discord.VoiceClient.average_latency) * 1000)}ms\nCurrent Latency: {round(int(discord.VoiceClient.latency) * 1000)}ms',
                inline=False
            )
        except:
            pass

        #print(str(self.client.db_name.command('ping')))
        #embed.add_field(
        #    name = f"<:mongo:792292784244916264> Database Latency:",
        #    value = self.client.db_name.command("ping"),
        #    inline=False
        #)
        embed.set_footer(text = f'Requested by: {ctx.author.name}#{ctx.author.discriminator}')
        await ctx.send(embed=embed)

    @commands.command()
    @typings
    async def man(self, ctx, *, page: str):
        """Returns the manual's page for a linux command used in the Terminal."""

        base_url = f'https://man.cx/{page}'
        url = urllib.parse.quote_plus(base_url, safe=';/?:@&=$,><-[]')

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(url) as response:
                if response.status != 200:
                    return await ctx.send(f'An error occurred (status code: {response.status}). Retry later.')

                soup = BeautifulSoup(await response.text(), 'lxml')

                nameTag = soup.find('h2', string='NAME\n')

                if not nameTag:
                    # No NAME, no page
                    return await ctx.send(f'No manual entry for `{page}`. (Debian)')

                # Get the two (or less) first parts from the nav aside
                # The first one is NAME, we already have it in nameTag
                contents = soup.find_all('nav', limit=2)[1].find_all('li', limit=3)[1:]

                try:
                    if contents[-1].string == 'COMMENTS':
                        contents.remove(-1)
                except ValueError:
                    return await ctx.send(f'No manual entry for `{page}`. (Debian)')

                title = self.get_content(nameTag)

                emb = discord.Embed(title=title, url=f'https://man.cx/{page}')
                emb.set_author(name='Debian Linux man pages')
                emb.set_thumbnail(url='https://www.debian.org/logos/openlogo-nd-100.png')

                for tag in contents:
                    h2 = tuple(soup.find(attrs={'name': tuple(tag.children)[0].get('href')[1:]}).parents)[0]
                    emb.add_field(name=tag.string, value=self.get_content(h2), inline=False)

                await ctx.send(embed=emb)

    @commands.command(aliases = ['uni'])
    @commands.guild_only()
    async def unicode(self, ctx, custom_emoji = None):
        if custom_emoji == None:
            await ctx.send("Hey! Please put the emoji to be needed to be converted to a Unicode!")
            return
        uni = str(custom_emoji)
        if uni.startswith("<"):
            await ctx.send(f"Here is the unicode for {custom_emoji}:\n`{uni}`")
        else:
            finalemoji = custom_emoji.replace(":", "")
            try:
                unic = get(ctx.guild.emojis, name = f"{finalemoji}")
            except:
                await ctx.send(f"`{str(custom_emoji)}` Emoji Not Found or Invalid!")
                return

            try:
                if unic.animated:
                    await ctx.send(f"Here is the unicode for {unic}:\n`<a:{finalemoji}:{str(unic.id)}>`")
                else:
                    await ctx.send(f"Here is the unicode for {unic}:\n`<:{finalemoji}:{str(unic.id)}>`")
            except:
                await ctx.send(f"`{str(custom_emoji)}` Emoji Not Found or Invalid!")
                return

    #@commands.command(aliases = ['sources', 'code', 'codes'])
    async def source(self, ctx, *, command: str = None):
        """
        Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        #chrome_options = Options()
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument('--no-sandbox')
        #driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)
        #driver2 = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)
        source_url = 'https://github.com/proguy914629bot/LyricMaster'
        branch = '1.0.0'

        if command is None:
            return await ctx.send(source_url + f'\n\nHint: You can specify a specific command to view the source of that command, Like `lm?source ping`!')

        obj = self.bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send(f"Command Named {command} Not Found!")

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        location = os.path.realpath(filename).replace("\\", '/')

        if "home/gilb" in location:
            await ctx.send("Command Found but Not Updated/Found in Github Repo. Here is the main link! {}!".format(source_url))
            return

        #if "/home/gilb/.local" in location:
        #    async with ctx.message.channel.typing():
        #        finallocation = location.replace("/home/gilb/.local/lib/python3.8/site-packages/", "")
        #        finallocation2 = finallocation.replace(" ", "+")
        #        driver2.get(f"https://www.google.com/search?q=pip+install+{finallocation2}")
        #
        #        pypipage = driver2.find_elements_by_css_selector("yuRUbf > a").__getattribute__('href')
        #
        #        print(pypipage)
        #
        #        driver.get(f'{str(pypipage)}')
        #
        #        pipcmd = driver.find_element_by_xpath('.//span[@class = "package-header__pip-instructions"]')[0]
        #
        #        print(pipcmd)

        #    finallocation = location.replace("/home/gilb/.local/lib/python3.8/site-packages/", "")
        #    finallocation2 = finallocation.replace(" ", "+")
        #    req = Request(f"https://www.google.com/search?q=pip+install+{finallocation2}", headers={'User-Agent': 'Mozilla/5.0'})
        #    webpage = urlopen(req).read()
        #    soup = BeautifulSoup(webpage, "html.parser")
        #    for link in soup.findAll('a', attrs={'href', re.compile("^https://pypi.com/")}):
        #        href = print(link.get('href'))

        #async with ClientSession() as session:
        #    async with session.get(f'{source_url}/blob/{branch}/{location}#L{firstlineno - 1}-L{firstlineno + len(lines) - 2}') as response:
        #        if response.status != 200:
        #            await ctx.send("Cannot connect to GitHub Servers. Try Again Later! Maybe check the Github Status. If not here is the main link! {}".format(source_url))
        #            return
        #        else:
        #            pass

        final_url = f'{source_url}/blob/{branch}/{location}#L{firstlineno - 1}-L{firstlineno + len(lines) - 2}'
        finalurl2 = final_url.replace('//home/gilb/LyricMaster/', '/')
        await ctx.send(finalurl2)

    def convert_size(self, bytes, suffix = "B"):
        """
Scale bytes to its proper format
e.g:
    1253656 => '1.20MB'
    1253656678 => '1.17GB'
        """
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"

            bytes /= factor

    @commands.command()
    async def botinfo(self, ctx):
        system = platform.uname()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_partitions()
        disk_io = psutil.disk_io_counters()
        embed = discord.Embed(
            title = "__**Bot Info:**__",
            description = "Here is the bot's info!"
        )
        embed.color = discord.Color.blue if ctx.author.color == 0 else ctx.author.color
        embed.add_field(
            name = "**System Info:**",
            value = f"""
- System: {str(system.system)}
- System Version: {str(system.version)}
- System Machine: {str(system.machine)}
            """
        )
        embed.add_field(
            name = "**Memory:**",
            value = f"""
Total: {self.convert_size(memory.total)}
Available/Free: {self.convert_size(memory.available)}
Used: {self.convert_size(memory.used)} | {memory.percent}%
            """
        )
        core = ""
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            core += f"- Core {i}: {percentage}%\n"

        embed.add_field(
            name = "**CPU Info**",
            value = f"""
Pysical Cores: {psutil.cpu_count(logical=False)}
Total Cores: {psutil.cpu_count(logical=True)}

CPU Usage Per Core:
{core}
            """
        )
        embed.add_field(
            name = "**Python Version:**",
            value = f"[{platform.python_version()}](https://www.python.org/downloads/release/python-{str(platform.python_version()).replace('.', '')}/)"
        )
        embed.add_field(
            name = "**Discord Version:**",
            value = f"[{str(discord.__version__)}](https://pypi.org/project/discord.py/{str(discord.__version__)}/)"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def invite(self, ctx):
        """
        Sends the invite link to invite the bot to your server
        """
        embed = discord.Embed(
            title = "Invite me Here using this link below!",
            color = ctx.author.color if ctx.author.color.value != 0 else discord.Color.blue(), 
            timestamp = ctx.message.created_at
        )
        embed.add_field(
            name = "Administrator Invite - Recommended:",
            value = "[Click Here!](https://discord.com/api/oauth2/authorize?client_id=755291533632077834&permissions=8&scope=bot)"
        )
        embed.add_field(
            name = "Non-Administrator Invite - Not Recommended:",
            value = "[Click Here!](https://discord.com/api/oauth2/authorize?client_id=755291533632077834&permissions=1152675008&scope=bot)"
        )
        await ctx.send(embed=embed)

    #@commands.group(aliases = ['link'])
    async def domain(self, ctx):
        """
        Sends the link to the LyricMaster's Domain Home Page
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(str(self.domainLink))

    #@domain.command(aliases = ['--search', 'search', '-search'])
    async def link_search(self, ctx, *, args = None):
        """
        Searces for stuff/things from LyricMaster's Domain Page
        """

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--no-sandbox')
        dri = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=chrome_options)

        if args == None:
            await ctx.send(f"Please put a search that you want to search in LyricMaster's Domain!")
            return

        searchlink = f"{str(self.domainLink)}_/search?query={str(args).replace(' ', '%20')}&scope=site"

        link = await check_url(searchlink)

        if False in link:
            await ctx.send("Nothing Found!")
            return
        
        async with ctx.message.channel.typing():

            dri.get(searchlink)

            try:
                desc = dri.find_elements_by_class_name("yDWqEe")[0].text
            except:
                await ctx.send("Nothing Found!")
                return

            totallink = dri.find_elements_by_class_name('yDWqEe')

            #links_with_text = []

            #req = Request("{}".format(searchlink))
            #webpage = urlopen(req).read()
            #soup = BeautifulSoup(webpage, 'html.parser')

            #for a in soup.find_all('a', href=True):
            #    if a.text:
            #        print(a)
            #        #print("---------------------")
            #        #li = list(a.split("\n"))
            #        #print(li)
            #        print("---------------------")
            #        li2 = list(str(a).split("\n"))
            #        print(li2)
            #        print("---------------------")
                    #print(li[1])
                    #print("---------------------")
            #        print(li2[1])
            #        links_with_text.append(a['href'])

            if len(totallink) == 1:
                embed = discord.Embed(
                    title = f'Search - "{str(args)}"',
                    description = f'{str(desc)}\n{str(dri.find_elements_by_class_name("sVLFaf")[0].text)}',
                    color = ctx.author.color,
                    timestamp = ctx.message.created_at,
                    url = f"{searchlink}"
                )
            else:
                await ctx.send(f"There are {len(totallink)} Options. `1` For the highest option and `{len(totallink)}` for the last option available. Please send a number for you to view.")

                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel

                answer = []

                try:
                    msg = await self.bot.wait_for('message', check=check, timeout = 60.0)
                except asyncio.TimeoutError:
                    await ctx.send("Took to long to reply to the message. Try again later!")
                else:
                    answer.append(msg.content)

                intanswer0 = int(answer[0])
                stranswer0 = str(answer[0])

                if intanswer0 <= 0:
                    await ctx.send("No option such as `{}`! Your option is too small!".format(stranswer0))
                    return

                if intanswer0 > len(totallink):
                    await ctx.send(f"No option such as `{stranswer0}`! Your opttion is too big!")
                    return

                try:
                    embed = discord.Embed(
                        title = f'Search - "{str(args)}"',
                        description = f'{str(totallink[round(intanswer0 - 1)].text)}\n\n{str(dri.find_elements_by_class_name("sVLFaf")[round(intanswer0 - 1)].text)}',
                        color = ctx.author.color,
                        timestamp = ctx.message.created_at,
                        url = f'{searchlink}'
                    )
                except IndexError:
                    await ctx.send(f"No option such as `{stranswer0}`! Your opttion is too big!")
                    return

            embed.set_footer(
                text = f"Source: \"{searchlink}\""
            )

            await ctx.send(embed=embed)

    #@commands.command(aliases = ['rtfd'])
    #async def rtfm(self, ctx, *, args):
    #    fianlarg = str(args).lower()
    #
    #    if "faq" in fianlarg:
    #        await ctx.send("https://lyricmaster.ayomerdeka.com/faq-qna")
    #        return
    #    elif "qna" in fianlarg:
    #        await ctx.send("https://lyricmaster.ayomerdeka.com/faq-qna")
    #        return
    #    elif "invite" in fianlarg:
    #        await ctx.send("https://lyricmaster.ayomerdeka.com/invite")
    #        return
    #    else:
    #        await ctx.send("That Argument {} Is not a Valid RTFM/RTFD!".format(args))
    #        return

def setup(bot):
    bot.add_cog(Bot_Related(bot))
    print('BotRelated Cog Is Ready!')
