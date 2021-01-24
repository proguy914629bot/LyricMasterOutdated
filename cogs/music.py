import discord
from discord.ext import commands
import lyrics_extractor
from lyrics_extractor import SongLyrics #pip install lyrics_extractor
import asyncio
import DiscordUtils
import lavalink
from discord.ext import flags
import os
import sys
import json
import spotipy
import webbrowser
import spotipy.util as util
from json.decoder import JSONDecodeError
import datetime
from discord.ext.buttons import Paginator
from discord.ext import menus

music = DiscordUtils.Music()

class Pag(Paginator):
    async def teardown(self):
        try:
            await self.page.clear_reactions()
        except discord.HTTPException:
            pass

def CheckVC(ctx):
    data = [m.id for m in ctx.voice_client.channel.members]
    return data

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.botID = 755291533632077834
        self.bot.music = lavalink.Client(self.botID)
        self.bot.music.add_node('localhost', 7000, 'testing', 'na', 'music-node')
        self.bot.add_listener(self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)
        self.clean_prefix = 'lm!'
        self.notjoinbotError = "You have no permissions to use this command! Please go to `{}` to use this command!"

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    #@commands.command()
    async def search(self, ctx, *, query = None):
        if query == None:
            await ctx.send("Missing required argument, `query`!")
            return
        if ctx.voice_client is not None:
            pass
        else:
            player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
            player.store('channel', ctx.channel.id)
            
            try:
                await ctx.author.voice.channel.connect() #Joins author's voice channel
            except:
                await ctx.send('<:xmark:780668123920465930> You are not in a voice channel.')
                return
            await ctx.send(f'<:check:780668111032418374> Joined `{ctx.author.voice.channel.name}`.')
        try:
            data = CheckVC(ctx)
            if ctx.author.id not in data:
                await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
                return
            player = self.bot.music.player_manager.get(ctx.guild.id)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:15]
            i = 0
            query_result = ''
            for track in tracks:
                i += 1
                query_result = query_result + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]})\n'
                i.song = query_result + f'{i}) [{track["info"]["title"]}]({track["info"]["uri"]})\n'
                i.url = track["info"]["uri"]
            embed = discord.Embed()
            embed.description = str(query_result)
            embed.footer = "Please enter a number from the list here!"

            await ctx.channel.send(embed=embed)
        except:
            await ctx.send("Nothing found...")
            return

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        response = await self.bot.wait_for('message', check=check)
        responseError = "Please enter a valid number from 1 to 10!"
        try:
            track = tracks[int(response.content)-1]
        except:
            await ctx.send(responseError)
            return

        if track >= 11:
            await ctx.send(responseError)
            return
        if track <= 0:
            await ctx.send(responseError)
            return

        players = music.get_player(guild_id=ctx.guild.id)
        if not players:
            players = music.create_player(ctx, ffmpeg_error_betterfix=True)
        if not ctx.voice_client.is_playing():
            await player.queue(track.url, bettersearch=True)
            song = await player.play()
            await ctx.send(f"<:check:780668111032418374> Now Playing `{song.name}`.")
        else:
            song = await player.queue(track.url, bettersearch=True)
            await ctx.send(f"<:check:780668111032418374> Queued `{song.name}`.")

    @commands.command(aliases = ['p'])
    async def play(self, ctx, *, url):
        f"""Plays music from a yt search or link.\nUsage: {self.clean_prefix}play <YT Search | YT URL>"""
        #if str(url).startswith("-"):
        #    if ctx.invoked_subcommand is None:
        #        await ctx.send("Invalid sub-command!")
        #        return
        if ctx.voice_client is None:
            try:
                await ctx.author.voice.channel.connect() #Joins author's voice channel
            except:
                await ctx.send('<:xmark:780668123920465930> You are not in a voice channel.')
                return
            await ctx.send(f'<:check:780668111032418374> Joined `{ctx.author.voice.channel.name}`.')

            #if 'spotify' in url:
            #    await ctx.send(f'Sorry. We don\'t accept Spotify URL\'s yet! Will soon!')
            #    return
            import random
            try:
                player = music.get_player(guild_id=ctx.guild.id)
                msg = await ctx.send(f'<a:loading:799207896779980830> Searching for `{url}` in YouTube...')
                await asyncio.sleep(random.randrange(3, 7))
                if not player:
                    player = music.create_player(ctx, ffmpeg_error_betterfix=True)
                if not ctx.voice_client.is_playing():
                    await player.queue(url, bettersearch=True)
                    song = await player.play()
                    #await ctx.send(f"Now Playing `{song.name}`.")
                    embed = discord.Embed(description = "[{}]({})".format(song.name, song.url), color = ctx.author.color if ctx.author.color != 0 else discord.Color.blue())
                    embed.add_field(name = "Channel:", value = "[{}]({})".format(song.channel, song.channel_url))
                    embed.set_author(name = f"Now Playing:", icon_url=ctx.author.avatar_url)
                    embed.add_field("Duration:", str(datetime.timedelta(seconds = int(song.duration))))
                    embed.set_footer("Requested by: {}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url=ctx.author.avatar_url)
                    #embed.add_field("")
                    await msg.edit(embed=embed)
                else:
                    song = await player.queue(url, bettersearch=True)
                    #nowplay = player.now_playing()
                    #embed = discord.Embed(description = "[{}]({})".format(song.name, song.url), color = ctx.author.color if ctx.author.color != 0 else discord.Color.blue())
                    #embed.add_field(name = "Channel:", value = "[{}]({})".format(song.channel, song.channel_url))
                    #embed.set_author(name = f"Queued:", icon_url=ctx.author.avatar_url)
                    #embed.add_field(name = "Duration:", value = str(datetime.timedelta(seconds = int(song.duration))))
                    #embed.add_field(name = "Estimated Time Until Playing:", value = str(datetime.timedelta(seconds = int(nowplay.duration))))
                    #embed.set_footer(text = "Requested by: {}#{}".format(ctx.author.name, ctx.author.discriminator), icon_url=ctx.author.avatar_url)
                    await ctx.send(f"<:check:780668111032418374> Queued `{song.name}`.")
                    #await msg.edit(embed=embed)
                    #await asyncio.sleep(int(nowplay.duration))
                    #em = discord.Embed(title = "Now Playing:", description = f"[{song.name}]({song.url})", color = ctx.author.color if ctx.author.color != 0 else discord.Color.blue())
                    #await ctx.send(embed=em)
            except Exception as e:
                await ctx.send('<:xmark:780668123920465930> Something went wrong whilst atempting to play the requested song.\n\nError: ```py\n{}\n```'.format(e))
        else:
            data = CheckVC(ctx)
            if ctx.author.id not in data:
                await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
                return
            try:
                player = music.get_player(guild_id=ctx.guild.id)
                if not player:
                    player = music.create_player(ctx, ffmpeg_error_betterfix=True)
                if not ctx.voice_client.is_playing():
                    await ctx.send(f'<:youtube_logo:779548294547505162> Searching for `{url}` in YouTube.. Please Wait')
                    await player.queue(url, bettersearch=True)
                    song = await player.play()
                    await ctx.send(f"<:check:780668111032418374> Now Playing `{song.name}`.")
                else:
                    await ctx.send(f'<:youtube_logo:779548294547505162> Searching for `{url}` in YouTube.. Please Wait')
                    song = await player.queue(url, bettersearch=True)
                    await ctx.send(f"<:check:780668111032418374> Queued `{song.name}`.")
            except Exception as e:
                await ctx.send('<:xmark:780668123920465930> Something went wrong whilst atempting to play the requested song.\n\nError: ```py\n{}\n```'.format(e))

    #@flags.add_flag("--spotify", type=str)
    #@play.command(cls=flags.FlagCommand)
    async def spotify_play_test(self, ctx, **flags):
        if ctx.voice_client is None:
            try:
                await ctx.author.voice.channel.connect() #Joins author's voice channel
            except:
                await ctx.send('<:xmark:780668123920465930> You are not in a voice channel.')
                return
            await ctx.send(f'<:check:780668111032418374> Joined `{ctx.author.voice.channel.name}`.')
        else:
            data = CheckVC(ctx)
            if ctx.author.id not in data:
                await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
                return
        spotify = "{spotify!r}".format(**flags)
        try:
            os.system("cd LyricMaster")
        except:
            pass

        try:
            os.system('spotdl "{}"'.format(spotify))
        except:
            await ctx.send("Nothing found on Spotify...")
            return

    #@flags.add_flag("--spotify", type=str)
    #@play.command(cls=flags.FlagCommand)
    async def play_spotify_test_two(self, ctx, **flags):
        username = sys.argv[1]
        scope = 'user-read-private user-read-playback-state user-modify-playback-state'
        try:
            token = util.prompt_for_user_token(username, scope)
        except (AttributeError, JSONDecodeError):
            os.remove(f".cache-{username}")
            token = util.prompt_for_user_token(username, scope)

        spotifyObject = spotipy.Spotify(auth=token)
        devices = spotifyObject.devices()
        print(json.dumps(devices, sort_keys=True, indent=4))
        deviceID = devices['devices'][0]['id']
        track = spotifyObject.current_user_playing_track()
        print(json.dumps(track, sort_keys=True, indent=4))
        print()
        artist = track['item']['artists'][0]['name']
        track = track['item']['name']

        if artist !="":
            print("Currently playing " + artist + " - " + track)

    @commands.command(aliases = ['j', 'summon'])
    async def join(self, ctx):
        f"""Joins your current voice channel: {ctx.author.voice.channel.name}\nUsage: {self.clean_prefix}join"""
        if ctx.voice_client != None:
            data = CheckVC(ctx)
            if ctx.author.id in data:
                await ctx.send("I am already in your voice channel!")
                return
            else:
                await ctx.send("I am currently in use! Please wait for me to finish my task!")
                return

        #player = self.bot.music.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        #player.store('channel', ctx.channel.id)

        try:
            await ctx.author.voice.channel.connect() #Joins author's voice channel
        except:
            await ctx.send('<:xmark:780668123920465930> You are not in a voice channel.')
            return
        await ctx.send(f'<:check:780668111032418374> Joined `{ctx.author.voice.channel.name}`.')

    @commands.command(aliases = ['disconnect'])
    async def leave(self, ctx):
        f"""Leaves the voice channel that the bot is in.\nUsage: {self.clean_prefix}leave"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        try:
            await ctx.voice_client.disconnect()
        except:
            await ctx.send(f'<:xmark:780668123920465930> I am not in a voice channel.')
            return
        await ctx.send('<:check:780668111032418374> Stopped playing music, and left the voice channel.')

    @commands.command()
    async def pause(self, ctx):
        f"""Pauses the current music playing.\nUsage: {self.clean_prefix}pause"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song = await player.pause()
            await ctx.send(f"⏯ Paused `{song.name}`")
        except:
            await ctx.send('<:xmark:780668123920465930> Nothing is in the queue.')

    @commands.command()
    async def resume(self, ctx):
        f"""Resumes the current music playing.\nUsage: {self.clean_prefix}resume"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song = await player.resume()
            await ctx.send(f"⏯ Resumed `{song.name}``")
        except:
            await ctx.send('<:xmark:780668123920465930> Nothing is in the queue.')

    @commands.command()
    async def stop(self, ctx):
        f"""Stops the current music playing.\nUsage: {self.clean_prefix}stop"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        player = music.get_player(guild_id=ctx.guild.id)
        await player.stop()
        await ctx.send("<:check:780668111032418374> Stopped playing music.")

    @commands.command(aliases = ['l'])
    async def loop(self, ctx):
        f"""Loops the current track/song that is playing.\nUsage: {self.clean_prefix}loop"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song = await player.toggle_song_loop()
            if song.duration == 0.0:
                await ctx.send('<:xmark:780668123920465930> Live videos can\'t be looped.')
            else:
                if song.is_looping:
                    await ctx.send(f"🔂  Now looping `{song.name}`")
                else:
                    await ctx.send(f"🔂  Disabled looping for `{song.name}`")
        except:
            await ctx.send('<:xmark:780668123920465930> Nothing is in the queue.')

    @commands.command(aliases = ['vol'])
    async def volume(self, ctx, vol):
        f"""Changes the current volume music.\nUsage: {self.clean_prefix}vol <Volume (Must Be 1 - 100)>"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song, volume = await player.change_volume(float(vol) / 100) # volume should be a float between 0 to 1
            await ctx.send(f"<:check:780668111032418374> Volume for {song.name} is set to {vol}%")
        except:
            await ctx.send('<:xmark:780668123920465930> Nothing is being played right now.')
            return

    @commands.command(aliases = ['rm'])
    async def remove(self, ctx, index):
        f"""Removes a song from the queue.\nUsage: {self.clean_prefix}remove <Queue Number (First song in the queue: 1, Second Song in the queue: 2, etc)>"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        player = music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index))
        await ctx.send(f"<:check:780668111032418374> Removed {song.name} from queue")

    @commands.command(aliases = ['q'])
    async def queue(self, ctx):
        f"""Views the queue of the song.\nUsage: {self.clean_prefix}queue"""
        player = music.get_player(guild_id=ctx.guild.id)
        embed = discord.Embed(
            color = discord.Color.gold(),
            title = f'Queue: ',
            description = f"{', '.join([song.name for song in player.current_queue()])}"
        )
        await ctx.send(embed=embed)

    @commands.command(aliases = ['nowplaying'])
    async def np(self, ctx):
        f"""Views the current playing music info.\nUsage: {self.clean_prefix}np"""
        try:
            player = music.get_player(guild_id=ctx.guild.id)
            song = player.now_playing()
            if song.duration == 0.0:
                embed = discord.Embed(
                    color = discord.Color.gold(),
                    title = '⏯️  Now Playing:',
                    description = f'[{song.name}]({song.url})'
                )
                embed.set_thumbnail(url = song.thumbnail)
                embed.add_field(name = 'Duration: ', value = f'LIVE', inline=True)
                embed.add_field(name = 'Channel Name: ', value = f'[{song.channel}]({song.channel_url})', inline=True)
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    color = discord.Color.gold(),
                    title = '⏯️  Now Playing:',
                    description = f'[{song.name}]({song.url})'
                )
                embed.set_thumbnail(url = song.thumbnail)
                embed.add_field(name = 'Duration: ', value = f'{str(datetime.timedelta(seconds = int(song.duration)))}', inline=True)
                embed.add_field(name = 'Being Looped? ', value = f'{song.is_looping}', inline=True)
                embed.add_field(name = 'Channel Name: ', value = f'[{song.channel}]({song.channel_url})', inline=True)
                await ctx.send(embed=embed)
        except:
            embed = discord.Embed(
                color = discord.Color.gold(),
                title = '⏯️  Now/Currently Playing:',
                description = f'<:xmark:780668123920465930> Nothing is in the queue.'
            )
            await ctx.send(embed=embed)

    @commands.command(aliases = ['fs', 'forceskip'])
    async def skip(self, ctx):
        f"""Skips the current song playing.\nUsage: {self.clean_prefix}skip"""
        data = CheckVC(ctx)
        if ctx.author.id not in data:
            await ctx.send(self.notjoinbotError.format(ctx.voice_client.channel.name))
            return
        player = music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        if len(data) == 2:
            await ctx.send(f"Skipped from `{data[0].name}` to `{data[1].name}`.")
        else:
            await ctx.send(f"Skipped `{data[0].name}`")

    @commands.command(aliases = ['lyrics'])
    async def lyric(self, ctx, *, songes = None):
        f"""Under Construction. Useable but not 100% Operational!\nViews the lyric for a specific song\nUsage: {self.clean_prefix}lyrics <Song Name (If None/Blank, it gets the current song playing lyrics)>"""
        async with ctx.message.channel.typing():
            extract_lyrics = SongLyrics('AIzaSyCd2mUKNe8eGbTvDfTgE8fdKEMvdt3vyYU', '3d527b3474c25fe39')
            try:
                if songes == None:
                    player = music.get_player(guild_id=ctx.guild.id)
                    song = player.now_playing()
                    if song.duration == 0.0:
                        embed = discord.Embed(
                            color = ctx.author.color,
                            title = f'🎵 Lyric - {song.name}',
                            description = f'We cannot detect lyrics of a LIVE Video!'
                        )
                        embed.set_thumbnail(url = song.thumbnail)
                        await ctx.send(embed=embed)
                    else:
                        lyrics = extract_lyrics.get_lyrics(str(song.name))
                        embed = discord.Embed(
                            color = ctx.author.color,
                            title = f'Lyric - {song.name}',
                            description = f"{lyrics['lyrics']}"
                        )
                        embed.set_thumbnail(url = song.thumbnail)
                        await ctx.send(embed=embed)
                else:
                    lyrics = extract_lyrics.get_lyrics(str(songes))
                    embed = discord.Embed(
                        color = ctx.author.color,
                        title = f'Lyric - {lyrics["title"]}',
                        description = f"{lyrics['lyrics']}"
                    )
                    await ctx.send(embed=embed)
            except lyrics_extractor.LyricScraperException:
                await ctx.send("No results found found. Sorry!")
                return

            #class LyricPag(menus.Menu):
            #    async def send_initial_message(self, ctx, channel):
            #        return await channel.send(embed = )

def setup(bot):
    bot.add_cog(Music(bot))
    print('Music Cog Is Ready!')