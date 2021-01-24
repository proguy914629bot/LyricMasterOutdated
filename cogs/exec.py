import discord
import io
import json
import os
from discord.ext import commands
import json
import contextlib
import textwrap
from traceback import format_exception
from discord.ext.buttons import Paginator
#from LyricMaster import lyric

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def clean_code(content):
    if str(content).startswith("```") and str(content).endswith("```"):
        return "\n".join(str(content).split("\n")[1:][:-1])
    else:
        return content

class Execute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ['exec', 'execute'], hidden=True)
    async def eval(self, ctx, *, code):
        if ctx.author.id == 699839134709317642 or ctx.author.id == 621266489596444672:
            
            codes1 = clean_code(code)

            local_variables = {
                "discord": discord,
                "commands": commands,
                "bot": self.bot,
                "client": self.bot,
                "self.client": self.bot,
                "self.bot": self.bot,
                "_ctx": ctx,
                "_message": ctx.message,
                "message": ctx.message,
                "ctx": ctx,
                "os": os,
                "json": json
                #"_lyricmaster": LyricMaster,
                #"lyricmaster": LyricMaster,
                #"LyricMaster": LyricMaster,
                #"_LyricMaster": LyricMaster
            }

            stdout = io.StringIO()

            try:
                with contextlib.redirect_stdout(stdout):
                    exec(
                        f"async def func():\n{textwrap.indent(codes1, '    ')}", local_variables,
                    )

                    obj = await local_variables["func"]()
                    result = f"{stdout.getvalue()}\n--- {obj}\n"
            except Exception as e:
                result = "".join(format_exception(e, e, e.__traceback__))

            pager = Pag(
                timeout=100,
                entries=[result[i: i + 2000] for i in range(0, len(result), 2000)],
                length=1,
                prefix="```py\n",
                suffix="```"
            )

            await pager.start(ctx)
        else:
            await ctx.send("You have no permission to run the Execute Command!")
            return

def setup(bot):
    bot.add_cog(Execute(bot))
    print("Execute Cog Is Ready!")
