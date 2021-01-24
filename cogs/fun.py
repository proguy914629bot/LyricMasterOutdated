import discord
from discord.ext import commands, menus
import asyncio
import random
import time
import os
import json

os.chdir("/home/gilb/LyricMaster/")

class SnakeMenu(menus.Menu):
    """
    Menu for snake game.
    """
    def __init__(self, player_ids, **kwargs):
        super().__init__(**kwargs)
        self.game = SnakeGame(empty="⬛")
        self.player_ids = player_ids
        self.direction = None
        self.task = None
        self.embed = None
        self.is_game_start = asyncio.Event()

    async def send_initial_message(self, ctx, channel):
        await self.refresh_embed()
        self.task = ctx.bot.loop.create_task(self.loop())
        return await channel.send(embed=self.embed)

    async def get_players(self):
        if not self.player_ids:
            return "anyone can control the game"
        players = [str(await self.ctx.bot.fetch_user(player_id)) for player_id in self.player_ids]
        if len(self.player_ids) > 10:
            first10 = "\n".join(player for player in players[:10])
            return f"{first10}\nand {len(players[10:])} more..."
        return "\n".join(str(player) for player in players)

    async def refresh_embed(self):
        self.embed = discord.Embed(title=f"Snake Game", description=self.game.show_grid(),
                                   colour=self.ctx.bot.embed_colour)
        self.embed.add_field(name="Players", value=await self.get_players())
        self.embed.add_field(name="Score", value=self.game.score)
        self.embed.add_field(name="Current Direction", value=self.direction)

    async def loop(self):
        await self.is_game_start.wait()
        while not self.game.lose:
            await asyncio.sleep(1.5)
            self.game.update(self.direction)
            await self.refresh_embed()
            await self.message.edit(embed=self.embed)
        self.embed.add_field(name="Game Over", value=self.game.lose)
        await self.message.edit(embed=self.embed)
        self.stop()

    def reaction_check(self, payload):
        if payload.message_id != self.message.id:
            return False

        if self.player_ids:  # only specific people can access the board
            if payload.user_id not in self.player_ids:
                return False
        else:
            if payload.user_id == self.ctx.bot.user.id:
                return False
        return payload.emoji in self.buttons

    @menus.button("⬆️")
    async def up(self, _):
        self.direction = "up"
        self.is_game_start.set()

    @menus.button("⬇️")
    async def down(self, _):
        self.direction = "down"
        self.is_game_start.set()

    @menus.button("⬅️")
    async def left(self, _):
        self.direction = "left"
        self.is_game_start.set()

    @menus.button("➡️")
    async def right(self, _):
        self.direction = "right"
        self.is_game_start.set()

    @menus.button("⏹️")
    async def on_stop(self, _):
        self.stop()

class TicTacToe:
    """
    Game class for tic-tac-toe.
    """
    __slots__ = ("player1", "player2", "ctx", "msg", "turn", "player_mapping", "x_and_o_mapping", "board")

    def __init__(self, ctx, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.ctx = ctx
        self.msg = None
        self.board = {'↖️': "⬜", '⬆️': "⬜", '↗️': "⬜",
                      '➡️': "⬜", '↘️': "⬜", '⬇️': "⬜",
                      '↙️': "⬜", '⬅️': "⬜", '⏺️': "⬜"}
        self.turn = random.choice([self.player1, self.player2])
        if self.turn == player1:
            self.player_mapping = {self.player1: "🇽", self.player2: "🅾️"}
            self.x_and_o_mapping = {"🇽": self.player1, "🅾️": self.player2}
            return
        self.player_mapping = {self.player2: "🇽", self.player1: "🅾️"}
        self.x_and_o_mapping = {"🇽": self.player2, "🅾️": self.player1}

    def show_board(self):
        return f"**Tic-Tac-Toe Game between `{self.player1}` and `{self.player2}`**\n\n" \
            f"🇽: `{self.x_and_o_mapping['🇽']}`\n🅾️: `{self.x_and_o_mapping['🅾️']}`\n\n" \
            f"{self.board['↖️']} {self.board['⬆️']} {self.board['↗️']}\n" \
            f"{self.board['⬅️']} {self.board['⏺️']} {self.board['➡️']}\n" \
            f"{self.board['↙️']} {self.board['⬇️']} {self.board['↘️']}\n\n"

    def switch_turn(self):
        if self.turn == self.player1:
            self.turn = self.player2
            return
        self.turn = self.player1

    async def loop(self):
        while True:
            try:
                move, user = await self.ctx.bot.wait_for(
                    "reaction_add",
                    check=lambda reaction, user: reaction.message.guild == self.ctx.guild
                    and reaction.message.channel == self.ctx.message.channel
                    and reaction.message == self.msg and str(reaction.emoji) in self.board.keys() and user == self.turn,
                    timeout=300
                )
            except asyncio.TimeoutError:
                await self.msg.edit(content=f"{self.show_board()}Game Over.\n**{self.turn}** took too long to move.")
                await self.ctx.send(f"{self.turn.mention} game over, you took too long to move. {self.msg.jump_url}")
                return
            if self.board[move.emoji] == "⬜":
                self.board[move.emoji] = self.player_mapping[self.turn]
            else:
                await self.msg.edit(content=f"{self.show_board()}**Current Turn**: `{self.turn}`\nThat place is already filled.")
                continue
            condition = (
                self.board['↖️'] == self.board['⬆️'] == self.board['↗️'] != '⬜',  # across the top
                self.board['⬅️'] == self.board['⏺️'] == self.board['➡️'] != '⬜',  # across the middle
                self.board['↙️'] == self.board['⬇️'] == self.board['↘️'] != '⬜',  # across the bottom
                self.board['↖️'] == self.board['⬅️'] == self.board['↙️'] != '⬜',  # down the left side
                self.board['⬆️'] == self.board['⏺️'] == self.board['⬇️'] != '⬜',  # down the middle
                self.board['↗️'] == self.board['➡️'] == self.board['↘️'] != '⬜',  # down the right side
                self.board['↖️'] == self.board['⏺️'] == self.board['↘️'] != '⬜',  # diagonal
                self.board['↙️'] == self.board['⏺️'] == self.board['↗️'] != '⬜',  # diagonal
            )
            if any(condition):
                await self.msg.edit(content=f"{self.show_board()}Game Over.\n**{self.turn}** won!")
                break
            if "⬜" not in self.board.values():
                await self.msg.edit(content=f"{self.show_board()}Game Over.\nIt's a Tie!")
                break
            self.switch_turn()
            await self.msg.edit(content=f"{self.show_board()}**Current Turn**: `{self.turn}`")

    async def start(self):
        self.msg = await self.ctx.send(f"{self.show_board()}Setting up the board...")
        for reaction in self.board.keys():
            await self.msg.add_reaction(reaction)
        await self.msg.edit(content=f"{self.show_board()}**Current Turn**: `{self.turn}`")
        await self.loop()

class Fun(commands.Cog):
    """
    Fun Commands to use
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['coin'])
    async def coinflip(self, ctx, guess):
        """
        A coinflip game where you need to guess what the coin faces too.\n`guess`: Your guess. Either `tail`, `side`, or `heads`
        """
        result = random.choices(population=["heads", "tails", "side"], weights=[0.45, 0.45, 0.01], k=1)[0]
        if str(guess).lower() == result:
            return await ctx.send("You flipped a coin and it landed on it's `{}`! Good Job!".format(random))
        await ctx.send(f"Too bad. You guess was wrong. You flipped a coin and got `{result}`...")

    @commands.command(aliases=["ttt", "tic-tac-toe", "tic_tac_toe"])
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.guild)
    async def tictactoe(self, ctx, *, player2: discord.Member):
        """
        Challenge someone to a game of tic-tac-toe.\n`player2` - The user to challenge.
        """
        if player2 == ctx.author:
            return await ctx.send(f"You can't challenge yourself {ctx.author.mention}.")
        if player2.bot:
            return await ctx.send(f"You can't challenge bots {ctx.author.mention}.")
        msg = await ctx.send(f"{player2.mention}, **{ctx.author}** has challenged you to a game of tic tac toe! Do you accept their challenge?")
        await msg.add_reaction("\N{WHITE HEAVY CHECK MARK}")
        await msg.add_reaction("\N{CROSS MARK}")
        try:
            response, _ = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda reaction, user: reaction.message.guild == ctx.guild
                and reaction.message.channel == ctx.message.channel
                and reaction.message == msg
                and str(reaction.emoji) in ["\N{WHITE HEAVY CHECK MARK}", "\N{CROSS MARK}"]
                and user == player2,
                timeout=300)
        except asyncio.TimeoutError:
            return await ctx.send(f"**{player2}** took too long to respond. {msg.jump_url}")
        if response.emoji == "\N{CROSS MARK}":
            return await ctx.send(f"**{player2}** has declined your challenge {ctx.author.mention}.")
        ttt = TicTacToe(ctx, ctx.author, player2)
        await ttt.start()

    @commands.command()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def snake(self, ctx, *, players = None):
        """
        Play a game of snake by yourself or with others in the guild.\n`args` - The users who can control the game. Set this to `--public` to allow anyone to control the game. You can also mention, put the ID, or the name of the person in the guild. Defaults to solo
        """
        async with ctx.channel.typing():
            if players != None:
                if str(players).lower() == '--public':
                    if ctx.guild == None:
                        await ctx.send("Not in a guild. Passing to solo gamemode.")

                        player_ids = set()
                    else:
                        player_ids = []
                else:
                    player_ids = set()
                    for arg in players:
                        player = await commands.MemberConverter().convert(ctx, arg)
                        if not player.bot:
                            player_ids.add(player.id)

                player_ids.add(ctx.author.id)
                menu = SnakeMenu(player_ids, clear_reactions_after=True)
                await menu.start(ctx, wait=True)

    @commands.command()
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def cookie(self, ctx, *, arg = None):
        """
        Yum yum. Here is a cookie to who reacts first!\n`arg`: Showing the leaderboard. Usage lm?cookie leaderboard | <Count (How many people to be displayed. Defaults to 5)>
        """
        if "lb" in str(arg).lower():
            if " | " not in str(arg):
                arg += " | 5"
            
            count = str(arg).split(" | ")
            if len(count) == 0 or len(count) == 1:
                return await ctx.send("Missing Required Arguments!")
            if len(count) >= 3:
                return await ctx.send("Too many argument inserted!")
            try:
                count = count[1]
            except IndexError:
                return await ctx.send("Missing Required Arguments!")

            with open("BotRecords/cookie.json", "r") as f:
                data = json.load(f)

            if str(ctx.guild.id) not in data:
                return await ctx.send("No Data available for this server/guild!")
            
            total = []
            leader_board = {}

            guild = str(ctx.guild.id)

            for item in data[guild]:
                name = int(item)
                seconds = item[name]
                leader_board[seconds] = name
                total.append(seconds)

            total = sorted(total,reverse=True)

            em = discord.Embed(
                title = f"Top {count} For Fastest Cookie Claimer",
                color = discord.Color.blue()
            )
            index = 1
            for amt in total:
                id_ = leader_board[amt]
                member = ctx.guild.get_member(id_)
                name = member.name
                em.add_field(
                    name = f"{index}. {name}",
                    value = f"{amt} Seconds",
                    inline=False
                )
                
                if index == count:
                    break
                else:
                    index += 1
                
            await ctx.send(embed=em)
            return

        if "leaderboard" in str(arg).lower():
            if " | " not in str(arg):
                arg += " | 5"
            
            count = str(arg).split(" | ")
            if len(count) == 0 or len(count) == 1:
                return await ctx.send("Missing Required Arguments!")
            if len(count) >= 3:
                return await ctx.send("Too many argument inserted!")
            try:
                count = count[2]
            except IndexError:
                return await ctx.send("Missing Required Arguments!")

            with open("BotRecords/cookie.json", "r") as f:
                data = json.load(f)

            if str(ctx.guild.id) not in data:
                return await ctx.send("No Data available for this server/guild!")
            
            total = []
            leader_board = {}

            guild = str(ctx.guild.id)

            for item in data[guild]:
                name = int(item)
                seconds = item[name]
                leader_board[seconds] = name
                total.append(seconds)

            total = sorted(total,reverse=True)

            em = discord.Embed(
                title = f"Top {count} For Fastest Cookie Claimer",
                color = discord.Color.blue()
            )
            index = 1
            for amt in total:
                id_ = leader_board[amt]
                member = ctx.guild.get_member(id_)
                name = member.name
                em.add_field(
                    name = f"{index}. {name}",
                    value = f"{amt} Seconds",
                    inline=False
                )
                
                if index == count:
                    break
                else:
                    index += 1
                
            await ctx.send(embed=em)
            return

        cookies = ["🍪", "🥠"]
        reaction = random.choices(cookies, weights=[0.9, 0.1], k=1)[0]
        embed = discord.Embed(description=f"First one to eat the {reaction} wins!", colour=discord.Color.blue())
        message = await ctx.send(embed=embed)
        await asyncio.sleep(4)
        for i in reversed(range(1, 4)):
            await message.edit(embed=discord.Embed(description=str(i), colour=discord.Color.blue()))
            await asyncio.sleep(1)
        await asyncio.sleep(random.randint(0, 3))  # for extra challenge :)
        await message.edit(embed=discord.Embed(description="Eat the cookie!", colour=discord.Color.blue()))
        await message.add_reaction(reaction)
        start = time.perf_counter()
        try:
            _, user = await ctx.bot.wait_for(
                "reaction_add",
                check=lambda _reaction, user: _reaction.message.guild == ctx.guild
                and _reaction.message.channel == ctx.message.channel
                and _reaction.message == message and str(_reaction.emoji) == reaction and user != ctx.bot.user
                and not user.bot,
                timeout=60,)
        except asyncio.TimeoutError:
            return await message.edit(embed=discord.Embed(description="No one ate the cookie...",
                                                          colour=ctx.bot.embed_colour))
        end = time.perf_counter()
        await message.edit(embed=discord.Embed(description=f"**{user}** ate the cookie in `{end - start:.3f}` seconds!",
                                               colour=discord.Color.blue()))

        with open("BotRecords/cookie.json", "r") as f:
            data = json.load(f)

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)][str(ctx.author.id)] = int(float(f"{end - start:.3f}"))

        with open("BotRecords/cookie.json", "w") as f:
            json.dump(data, f, indent=4)

def setup(bot):
    bot.add_cog(Fun(bot))
    print("Fun Cog Is Ready!")