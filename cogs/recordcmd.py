import discord
from pathlib import Path
from typing import Optional
import asyncio
import random
import pyttsx3

import gtts
import pydub
import speech_recognition
from discord.ext import commands, tasks
import json
import ctypes
import ctypes.util

number_txt_file = Path.cwd() / 'number.txt'
number_txt_file.touch(exist_ok=True)
number = int(number_txt_file.open('r').read() or 0)
waves_folder = (Path.cwd() / 'recordings')
waves_file_format = "recording{}.wav"
waves_folder.mkdir(parents=True, exist_ok=True)
tts_folder = (Path.cwd() / 'tts')
tts_folder.mkdir(parents=True, exist_ok=True)
tts_file_format = "tts{}{}.mp3"
sr_folder = (Path.cwd() / 'sr')
sr_folder.mkdir(parents=True, exist_ok=True)
sr_file_format = "sr{}{}.wav"
engine = pyttsx3.init()
discord.opus.load_opus(ctypes.util.find_library('opus'))

async def talk(text):
    engine.say(text)
    engine.runAndWait()

class Recordings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def record(self, ctx):
        f"""Records a Voice Channel that you are in.\nUsage: lm!record"""
        if not ctx.author.voice:
            await ctx.send("Please join a Voice Channel before running this command {}!".format(ctx.author.mention))
            return
        
        botprofile = ctx.guild.me
        with open('BotRecords/recordstatus.json', 'r') as f:
            data = json.load(f)
        try:
            if data[str(ctx.guild.id)] in data:
                wave_files = waves_folder / waves_file_format.format(number)
                fps = wave_files.open('rb')
                if ctx.author.voice == botprofile.voice:
                    ctx.voice_client.stop_listening()
                    await ctx.send(f"Recording has been stopped by {ctx.author.mention} and being processed to be sent. Please wait!")
                    await asyncio.sleep(random.randrange(1, 10))
                    await ctx.send('Here\'s, your record file!', file=discord.File(fps, filename=str(wave_files.name)))
                    try:
                        await botprofile.edit(nick = f'{str(data[str(ctx.guild.id)]["Nickname"])}')
                    except:
                        pass
                    await talk(f'Recording has been sucsessfully stopped and the file has been sent in {str(ctx.channel.name)}. Leaving Voice Channel. Goodbye.')
                    await ctx.voice_client.disconnect()
                else:
                    await ctx.send(f'Please join the same voice channel that the bot is in to run this command!')
                return
        except:
            pass

        if not ctx.voice_client:
            vc = await ctx.author.voice.channel.connect()
            await ctx.send(f'Joined `{str(ctx.author.voice.channel.name)}`!')

        wave_file = waves_folder / waves_file_format.format(number)
        wave_file.touch()
        fp = wave_file.open('rb')
        await talk('Recording starting in, 3')
        await talk('2')
        await talk('1')
        await talk('Recording Started.')
        await ctx.send(f'Recording Started!')
        vc.listen(discord.WaveSink(str(wave_file)))
        botdn = str(botprofile.display_name)
        try:
            await botprofile.edit(nick = f"⏺ Recording | {botdn}")
        except:
            pass

        data[str(ctx.guild.id)] = {}
        data[str(ctx.guild.id)]["Status"] = "True"
        data[str(ctx.guild.id)]["Nickname"] = botdn

        with open('BotRecords/recordstatus.json', 'w') as f:
            json.dump(data, f, indent=4)

def setup(bot):
    bot.add_cog(Recordings(bot))
    print('Record Command Is Ready!')