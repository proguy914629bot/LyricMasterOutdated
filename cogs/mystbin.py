import discord
import mystbin
from discord.ext import commands
import json
import os
import aiohttp
import asyncio
import yarl
import re

os.chdir("/home/gilb/LyricMaster/BotRecords/")

class GithubError(commands.CommandError):
    pass

class Github_Related(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._req_lock = asyncio.Lock(loop=self.bot.loop)

    async def github_request(self, method, url, *, params=None, data=None, headers=None):
        with open("BotInfo.json", "r") as f:
            data = json.load(f)

        hdrs = {
            'Accept': 'application/vnd.github.inertia-preview+json',
            'User-Agent': 'RoboDanny DPYExclusive Cog',
            'Authorization': f'token {data["github-key"]}'
        }

        req_url = yarl.URL('https://api.github.com') / url

        if headers is not None and isinstance(headers, dict):
            hdrs.update(headers)

        await self._req_lock.acquire()
        try:
            async with self.bot.session.request(method, req_url, params=params, json=data, headers=hdrs) as r:
                remaining = r.headers.get('X-Ratelimit-Remaining')
                js = await r.json()
                if r.status == 429 or remaining == '0':
                    # wait before we release the lock
                    delta = discord.utils._parse_ratelimit_header(r)
                    await asyncio.sleep(delta)
                    self._req_lock.release()
                    return await self.github_request(method, url, params=params, data=data, headers=headers)
                elif 300 > r.status >= 200:
                    return js
                else:
                    raise GithubError(js['message'])
        finally:
            if self._req_lock.locked():
                self._req_lock.release()

    async def create_gist(self, content, *, description=None, filename=None, public=True):
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }

        filename = filename or 'output.txt'
        data = {
            'public': public,
            'files': {
                filename: {
                    'content': content
                }
            }
        }

        if description:
            data['description'] = description

        js = await self.github_request('POST', 'gists', data=data, headers=headers)
        return js['html_url']

    async def redirect_attachments(self, message):
        try:
            with open("mystbin.json", "r") as f:
                data = json.load(f)

            if str(message.guild.id) not in data:
                return

            if data[str(message.guild.id)] == "True":
                pass
            else:
                return

            attachment = message.attachments[0]
            if not attachment.filename.endswith(('.txt', '.py', '.json', '.js')):
                return

            # If this file is more than 2MiB then it's definitely too big
            if attachment.size > (2 * 1024 * 1024):
                return

            try:
                contents = await attachment.read()
                contents = contents.decode('utf-8')
            except (UnicodeDecodeError, discord.HTTPException):
                return

            description = f'A file by {message.author} in the discord.py guild'
            gist = await self.create_gist(contents, description=description, filename=attachment.filename)
            await message.channel.send(f'File automatically uploaded to gist: <{gist}>')
        except FileNotFoundError:
            pass

    @commands.Cog.listener()
    async def on_message(self, message):
        if len(message.attachments) == 0:
            pass
        if len(message.attachments) == 1:
            return await self.redirect_attachments(message)
        else:
            pass

    @commands.command(aliases = ['gist'])
    @commands.guild_only()
    @commands.has_guild_permissions(administrator=True)
    async def github(self, ctx, args = None):
        if args == None:
            await ctx.send("Args Accepted: `lm?github toggle`, `lm?github link`!")
            return
        
        finalargs = str(args).lower()

        if finalargs == "toggle":
            with open("mystbin.json", "r") as f:
                data = json.load(f)

            if str(ctx.guild.id) not in data:
                data[str(ctx.guild.id)] = "True"

                await ctx.send("Okay! I have enabled MystBin Extension for you!")

            else:
                if data[str(ctx.guild.id)] == "False":
                    data[str(ctx.guild.id)] = "True"

                    await ctx.send("Okay! I have disabled MystBin Extension for you!")

                else:
                    data[str(ctx.guild.id)] = "False"

                    await ctx.send("Okay! I have enabled MystBin Extension for you!")

            with open("mystbin.json", "w") as f:
                json.dump(data, f, indent=4)
        elif finalargs == "link":
            return await ctx.send('https://mystb.in/')
        else:
            await ctx.send(f"Args {str(args).title()} Not Accepted! Try doing `lm?github`!")
            return

def setup(bot):
    bot.add_cog(Github_Related(bot))
    print("Github Cog Is Ready!")