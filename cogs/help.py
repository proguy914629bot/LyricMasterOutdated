import discord
from discord.ext import commands, menus
import contextlib
import inspect
import json
import re
import humanize
import datetime
import textwrap
import more_itertools
import ctypes
import sys
import traceback
import datetime
import random
from collections import namedtuple
from discord.ext.menus import First, Last, Button
import asyncio
from discord.utils import maybe_coroutine

CommandHelp = namedtuple("CommandHelp", 'command brief')

def print_exception(text, error):
    """Prints the exception with proper traceback."""
    print(text, file=sys.stderr)
    traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    etype = type(error)
    trace = error.__traceback__
    lines = traceback.format_exception(etype, error, trace)
    return "".join(lines)

class MenuBase(menus.MenuPages):
    """This is a MenuPages class that is used every single paginator menus. All it does is replace the default emoji
       with a custom emoji, and keep the functionality."""
    def __init__(self, source, dict_emoji=None, **kwargs):
        super().__init__(source, delete_message_after=kwargs.pop('delete_message_after', True), **kwargs)
        self.info = False

        # Remind me to redo this dumb code
        EmojiB = namedtuple("EmojiB", "emoji position explain")
        def_dict_emoji = {'\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f':
                          EmojiB("<:fast_forward_left:802368686547271741>", First(0),
                                 "Goes to the first page."),

                          '\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f':
                          EmojiB("<a:facing_left_arrow:799579706688667669>", First(1),
                                 "Goes to the previous page."),

                          '\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f':
                          EmojiB("<a:facing_right_arrow:799579865296535583>", Last(1),
                                 "Goes to the next page."),

                          '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f':
                          EmojiB("<:fast_forward_left:802368686547271741>", Last(2),
                                 "Goes to the last page."),

                          '\N{BLACK SQUARE FOR STOP}\ufe0f':
                          EmojiB("⏹️", Last(0),
                                 "Remove this message.")
                          }
        self.dict_emoji = dict_emoji or def_dict_emoji
        for emoji in self.buttons:
            callback = self.buttons[emoji].action
            if emoji.name not in self.dict_emoji:
                continue
            new_but = self.dict_emoji[emoji.name]
            new_button = Button(new_but.emoji, callback, position=new_but.position)
            del self.dict_emoji[emoji.name]
            self.dict_emoji[new_but.emoji] = new_but
            self.add_button(new_button)
            self.remove_button(emoji)

    async def _get_kwargs_from_page(self, page):
        value = await discord.utils.maybe_coroutine(self._source.format_page, self, page)
        no_ping = {'allowed_mentions': discord.AllowedMentions(replied_user=False)}
        if isinstance(value, dict):
            value.update(no_ping)
        elif isinstance(value, str):
            no_ping.update({'content': value})
        elif isinstance(value, discord.Embed):
            no_ping.update({'embed': value, 'content': None})
        return no_ping

    def generate_page(self, content, maximum):
        if maximum > 1:
            page = f"Page {self.current_page + 1}/{maximum}"
            if isinstance(content, discord.Embed):
                return content.set_author(name=page)
            elif isinstance(content, str):
                return f"{page}\n{content}"
        return content

    async def send_initial_message(self, ctx, channel):
        page = await self._source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        return await ctx.reply(**kwargs)


class BaseEmbed(discord.Embed):
    """Main purpose is to get the usual setup of Embed for a command or an error embed"""
    def __init__(self, color=discord.Color.blue(), timestamp=None, **kwargs):
        super().__init__(color=color, timestamp=timestamp or datetime.datetime.utcnow(), **kwargs)

    @classmethod
    def default(cls, ctx, **kwargs):
        instance = cls(**kwargs)
        instance.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        return instance

    @classmethod
    def to_error(cls, title="Error", color=discord.Color.red(), **kwargs):
        return cls(title=title, color=color, **kwargs)

class HelpMenuBase(MenuBase):
    """This is a MenuPages class that is used every single paginator menus. All it does is replace the default emoji
       with a custom emoji, and keep the functionality."""

    def __init__(self, source, **kwargs):
        EmojiB = namedtuple("EmojiB", "emoji position explain")
        help_dict_emoji = {'\N{BLACK LEFT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f':
                           EmojiB("<:fast_forward_left:802368686547271741>", First(0),
                                  "Goes to the first page."),

                           '\N{BLACK LEFT-POINTING TRIANGLE}\ufe0f':
                           EmojiB("<a:facing_left_arrow:799579706688667669>", First(1),
                                  "Goes to the previous page."),

                           '\N{BLACK RIGHT-POINTING TRIANGLE}\ufe0f':
                           EmojiB("<a:facing_right_arrow:799579865296535583>", Last(1),
                                  "Goes to the next page."),

                           '\N{BLACK RIGHT-POINTING DOUBLE TRIANGLE WITH VERTICAL BAR}\ufe0f':
                           EmojiB("<:fast_forward_right:802368548482580510>", Last(2),
                                  "Goes to the last page."),

                           '\N{BLACK SQUARE FOR STOP}\ufe0f':
                           EmojiB("⏹️", Last(0),
                                  "Remove this message."),

                           '<:info:802371695725117461>':
                           EmojiB("<:info:802371695725117461>", Last(4),
                                  "Shows this infomation message.")}
        super().__init__(source, dict_emoji=help_dict_emoji, **kwargs)

    async def show_page(self, page_number):
        self.info = False
        await super().show_page(page_number)

    @menus.button('<:info:802371695725117461>', position=Last(4))
    async def on_information(self, payload):
        if info := not self.info:
            await self.on_information_show(payload)
        else:
            self.current_page = max(self.current_page, 0)
            await self.show_page(self.current_page)
        self.info = info

    async def on_information_show(self, payload):
        raise NotImplementedError("Information is not implemented.")

class HelpMenu(HelpMenuBase):
    """This is a MenuPages class that is used only in help command. All it has is custom information and
       custom initial message."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._current_wait = None
        self.help_command = None

    async def on_information_show(self, payload):
        ctx = self.ctx
        exists = [str(emoji) for emoji in super().buttons]
        embed = BaseEmbed.default(ctx,
                                  title="Information",
                                  description="This shows each commands that LyricMaster has to offer. Each page is a category that shows "
                                              "what commands that the category have.")
        curr = self.current_page + 1 if (p := self.current_page > -1) else "cover page"
        pa = "page" if p else "the"
        embed.set_author(icon_url=ctx.bot.user.avatar_url,
                         name=f"You were on {pa} {curr}")
        nav = '\n'.join(f"{self.dict_emoji[e].emoji} {self.dict_emoji[e].explain}" for e in exists)
        embed.add_field(name="Navigation:", value=nav)
        await self.message.edit(embed=embed, allowed_mentions=discord.AllowedMentions(replied_user=False))

    async def background_update(self):
        """Makes a help menu triggers every time a command is remove while active"""
        if not hasattr(self._source, "wait_for_update"):
            return
        while self._running:
            try:
                bot = self.ctx.bot
                command = await bot.wait_for("command_remove")
                if not self._running:
                    break
                if not await self._source.wait_for_update(self, command):
                    continue
            except Exception as e:
                print_exception("background_update fucking dies", e)
            else:
                self._source._max_pages = len(self._source.entries)
                await self.show_page(min(self.current_page, self._source._max_pages - 1))

    async def start(self, ctx, **kwargs):
        self.help_command = ctx.bot.help_command
        self.help_command.context = ctx
        self._current_wait = ctx.bot.loop.create_task(self.background_update())
        await super().start(ctx, **kwargs)

    def stop(self):
        super().stop()
        self._current_wait.cancel()

def plural(text, size):
    """Auto corrects text to show plural or singular depending on the size number."""
    logic = size == 1
    target = (("(s)", ("s", "")), ("(is/are)", ("are", "is")))
    for x, y in target:
        text = text.replace(x, y[logic])
    return text

def listToString(s):  
    
    # initialize an empty string 
    str1 = ""  
    
    # traverse in the string   
    for ele in s:  
        str1 += f"- `{ele}`\n"

    # return string   
    return str(str1)

class HelpSource(menus.ListPageSource):
    """This is for the help command ListPageSource"""
    def COLOUR(self, menu):
        if menu.ctx.author.color.value == 0:
            num = random.randrange(1, 3)
            if num == 1:
                return discord.Color.random()
            else:
                return discord.Color.blue() 
        else: 
            return menu.ctx.author.color

    async def format_page(self, menu: HelpMenu, entry):
        cog, list_commands = entry
        new_line = "\n"
        embed = discord.Embed(title=f"{getattr(cog, 'qualified_name', 'No')} Category",
                              description=new_line.join(f'{command_help.command}{new_line}{command_help.brief}'
                                                        for command_help in list_commands))
        try:
            embed.color = self.COLOUR(menu)
        except:
            embed.color = discord.Color.blue()
        author = menu.ctx.author
        embed.set_footer(text=f"Requested by {author}", icon_url=author.avatar_url)

        return menu.generate_page(embed, self._max_pages)

    async def wait_for_update(self, menu, command):
        """Makes the help command responsive, I do this for the hell of it I'm bored."""
        cog_name = getattr(command.cog, "qualified_name", None)
        command = CommandHelp(menu.help_command.get_command_signature(command), "")

        def find_command(iterable):
            return discord.utils.find(lambda current: command.command == current.command, iterable)

        def find_cog_command(value):
            cogs, list_of_commands = value
            return getattr(cogs, "qualified_name", None) == cog_name and find_command(list_of_commands)
        _, list_commands = discord.utils.find(find_cog_command, self.entries)
        i, _ = discord.utils.find(lambda x: x[1].command == command.command, enumerate(list_commands))
        del list_commands[i]
        if not list_commands:
            index, _ = discord.utils.find(lambda x: not bool(x[1][1]), enumerate(self.entries))
            del self.entries[index]
        return True

class CogMenu(HelpMenu):
    """This is a MenuPages class that is used only in Cog help command. All it has is custom information and
       custom initial message."""
    async def on_information_show(self, payload):
        ctx = self.ctx
        exists = [str(emoji) for emoji in super().buttons]
        embed = BaseEmbed.default(ctx,
                                  title="Information",
                                  description="This shows each commands in this category. Each page is a command that shows "
                                              "what's the command is about and a demonstration of usage.")
        curr = self.current_page + 1 if (p := self.current_page > -1) else "cover page"
        pa = "page" if p else "the"
        embed.set_author(icon_url=ctx.bot.user.avatar_url,
                         name=f"You were on {pa} {curr}")
        nav = '\n'.join(f"{self.dict_emoji[e].emoji} {self.dict_emoji[e].explain}" for e in exists)
        embed.add_field(name="Navigation:", value=nav)
        await self.message.edit(embed=embed, allowed_mentions=discord.AllowedMentions(replied_user=False))

class HelpCogSource(menus.ListPageSource):
    """This is for help Cog ListPageSource"""
    def __init__(self, *args, cog=None):
        super().__init__(*args, per_page=1)
        self.cog = cog

    async def format_page(self, menu: CogMenu, entry):
        return menu.generate_page(entry, self._max_pages)

    async def wait_for_update(self, menu, command):
        """Makes cog menu responsive"""
        if getattr(command.cog, "qualified_name", None) != self.cog:
            return
        signature = menu.help_command.get_command_signature(command)
        i, _ = discord.utils.find(lambda entry: entry[1].title == signature, enumerate(self.entries))
        del self.entries[i]
        return True

class LyricMasterHelp(commands.DefaultHelpCommand):
    def __init__(self, **options):
        super().__init__(**options)

    def get_command_signature(self, command, ctx=None):
        """Method to return a commands name and signature"""
        if not ctx:
            if not command.signature and not command.parent:
                return f'`{self.clean_prefix}{command.name}`'
            if command.signature and not command.parent:
                return f'`{self.clean_prefix}{command.name}` `{command.signature}`'
            if not command.signature and command.parent:
                return f'`{self.clean_prefix}{command.parent}` `{command.name}`'
            else:
                return f'`{self.clean_prefix}{command.parent}` `{command.name}` `{command.signature}`'
        else:
            def get_invoke_with():
                msg = ctx.message.content
                escape = "\\"
                prefixmax = re.match(f'{escape}{escape.join(ctx.prefix)}', msg).regs[0][1]
                return msg[prefixmax:msg.rindex(ctx.invoked_with)]

            if not command.signature and not command.parent:
                return f'{ctx.prefix}{ctx.invoked_with}'
            if command.signature and not command.parent:
                return f'{ctx.prefix}{ctx.invoked_with} {command.signature}'
            if not command.signature and command.parent:
                return f'{ctx.prefix}{get_invoke_with()}{ctx.invoked_with}'
            else:
                return f'{ctx.prefix}{get_invoke_with()}{ctx.invoked_with} {command.signature}'

    def COLOUR(self):
        if self.context.author.color.value == 0:
            num = random.randrange(1, 3)
            if num == 1:
                return discord.Color.random()
            else:
                return discord.Color.blue() 
        else: 
            return self.context.author.color

    def get_help(self, command, brief=True):
        """Gets the command short_doc if brief is True while getting the longer help if it is false"""
        real_help = command.help or "This command is not documented."
        return real_help if not brief else command.short_doc or real_help + '\n'

    def get_aliases(self, command):
        """Get the Command's Aliases."""
        return command.aliases

    def get_flag_help(self, command):
        """Gets the flag help if there is any."""
        def c(x):
            return "_OPTIONAL" not in x.dest
        return ["**--{0.dest}:** {0.help}".format(action) for action in command.callback._def_parser._actions if c(action)]

    async def send_bot_help(self, mapping):
        """Gets called when `lm?help` is invoked"""
        def get_info(com):
            return (getattr(self, f"get_{x}")(com) for x in ("command_signature", "help"))

        command_data = []

        for cog, unfiltered_commands in mapping.items():
            list_commands = await self.filter_commands(unfiltered_commands, sort=True)
            for chunks in more_itertools.chunked(list_commands, 6):
                command_data.append((cog, [CommandHelp(*get_info(command)) for command in chunks]))

        pages = HelpMenu(source=HelpSource(command_data, per_page=1), delete_message_after=True)
        with contextlib.suppress(discord.NotFound, discord.Forbidden):
            await pages.start(self.context, wait=True)
            await self.context.message.add_reaction("<a:TickGif:802378817325760593>")

    def get_command_help(self, command):
        embed = discord.Embed(
            color = self.COLOUR()
        )
        embed.title = f"{str(command.qualified_name).title()} Command"
        embed.description = f'{command.short_doc}' or ''
        embed.add_field(
            name = "Usage:",
            value = f"{str(self.get_command_signature(command))}"
        )
        try:
            embed.add_field(
                name = f'{str(len(command.aliases))} Aliases:' if len(command.aliases) >= 2 else f"{str(len(command.aliases))} Alias:", value = f'{listToString(command.aliases) if listToString(command.aliases) != "" else "No Aliases Found."}', inline = False
            )
        except:
            embed.add_field(
                name = "Aliases:", value = 'No Aliases Found.' 
            )
        embed.add_field(
            name = "In Cog:", value = str(command.cog_name) if command.cog_name != None or command.cog_name != "" else "Comamnd is not in a cog!", inline = False
        )
        try:
            embed.add_field(
                name = "Cooldown:",
                value = f"""
Seconds: {str(command._buckets._cooldown.per).replace(".0", "")}s
How many commands can be runned before the cooldown hits: {str(command._buckets._cooldown.rate)}
Type: Each {str(command._buckets._cooldown.type).replace("commands.", "").replace("BucketType.", "").replace("discord", "").replace("ext", "").replace(".", "").title()}
                """,
                #value = f"{str(command._buckets._cooldown)}s" if command.cooldown != 0.0 else "No Cooldown for this Command!",
                inline = False
            )
        except:
            embed.add_field(
                name = "Cooldown:",
                value = f"""
Seconds: 0s
                """,
                inline = False
            )
        if hasattr(command.callback, "_def_parser"):
            embed.add_field(name="Optional Flags:", value="\n".join(self.get_flag_help(command)), inline=False)

        if isinstance(command, commands.Group):
            subcommand = command.commands
            value = "\n".join(self.get_command_signature(c) for c in subcommand)
            embed.add_field(name=plural("Subcommand(s)", len(subcommand)), value=value)

        return embed

    async def handle_help(self, command):
        with contextlib.suppress(commands.CommandError):
            await command.can_run(self.context)
            return await self.context.reply(embed=self.get_command_help(command), mention_author=False)
        await self.context.reply("You don't have enough permission to see this help.", mention_author=False)

    async def send_command_help(self, command):
        """Gets invoked when `lm?help <command>` is invoked."""
        await self.handle_help(command)

    async def send_group_help(self, group):
        """Gets invoked when `lm?help <group>` is invoked."""
        await self.handle_help(group)

    async def send_cog_help(self, cog):
        """Gets invoked when `lm?help <cog/category>` is invoked."""
        cog_commands = [self.get_command_help(c) for c in await self.filter_commands(cog.walk_commands(), sort=True)]
        pages = CogMenu(source=HelpCogSource(cog_commands, cog=getattr(cog, "qualified_name", None)), delete_message_after=True)
        await pages.start(self.context)

class InputHelpToBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        bot.help_command = LyricMasterHelp()
        bot.help_command.cog = self
        self._default_help_command = bot.help_command

def setup(bot):
    bot.add_cog(InputHelpToBot(bot))
    print("Help Cog Is Ready!")