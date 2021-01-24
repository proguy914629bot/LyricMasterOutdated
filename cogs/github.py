import discord
from discord.ext import commands
import re
import aiohttp
import asyncio
import yarl
import base64
import binascii

class GithubError(commands.CommandError):
    pass

class Gist_Github(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._req_lock = asyncio.Lock(loop=self.bot.loop)
        self.TOKEN_REGEX = re.compile(r'[a-zA-Z0-9_-]{23,28}\.[a-zA-Z0-9_-]{6,7}\.[a-zA-Z0-9_-]{27}')

    async def github_request(self, method, url, *, params=None, data=None, headers=None):
        hdrs = {
            'Accept': 'application/vnd.github.inertia-preview+json',
            'User-Agent': 'LyricMaster Discord Bot',
            'Authorization': f'token {self.bot.github_token}'
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

    def validate_token(self, token):
        try:
            # Just check if the first part validates as a user ID
            (user_id, _, _) = token.split('.')
            user_id = int(base64.b64decode(user_id, validate=True))
        except (ValueError, binascii.Error):
            return False
        else:
            return True

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id == self.bot.user.id:
            return
        
        if message.author.bot:
            return

        tokens = [token for token in self.TOKEN_REGEX.findall(message.content) if self.validate_token(token)]

        if tokens and message.author.id != self.bot.user.id:
            url =  await self.create_gist('\n'.join(tokens), description='Discord tokens detected', filename="ALERT!.txt", public=True)
            msg = f'{message.author.mention}, I have found tokens and sent them to <{url}> to be invalidated for you.'
            return await message.channel.send(msg)

def setup(bot):
    bot.add_cog(Gist_Github(bot))