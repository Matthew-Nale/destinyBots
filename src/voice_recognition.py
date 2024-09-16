import discord
import os
import wave
import string
import openai
import asyncio
import io
import aiohttp
import shlex
import subprocess
import random
import json

from src.bot import Bot
from discord.opus import Encoder
from discord import app_commands
from datetime import datetime
from discord.ext import voice_recv, commands, tasks

INSTRUCTION_PROMPT = ("You are in a Discord call with other members, and you will be provided "
                     "the different users as well as what they said. Address the person you are speaking to. "
                     "The ordering of the sentences and users may not correspond with the actual "
                     "spoken order. Only respond with any input you may have, limiting your response to under 250 characters.")

MAX_LISTENS = 5
MIN_LISTENS = 3
LISTEN_TIME = 4
JOIN_CHANCE = 0.15
COOLDOWN_TIME_HOURS = 1
MAX_JOIN_LIMIT = 3

# Needed for specific streaming AudioSource
class StreamingAudio(discord.AudioSource):
    def __init__(self, source, *, executable='ffmpeg', pipe=False, stderr=None, before_options=None, options=None):
        stdin = None if not pipe else source
        args = [executable]
        if isinstance(before_options, str):
            args.extend(shlex.split(before_options))
        args.append('-i')
        args.append('-' if pipe else source)
        args.extend(('-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning'))
        if isinstance(options, str):
            args.extend(shlex.split(options))
        args.append('pipe:1')
        self._process = None
        try:
            self._process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderr)
            self._stdout = io.BytesIO(
                self._process.communicate(input=stdin)[0]
            )
        except FileNotFoundError:
            raise discord.ClientException(executable + ' was not found.') from None
        except subprocess.SubprocessError as exc:
            raise discord.ClientException('Popen failed: {0.__class__.__name__}: {0}'.format(exc)) from exc
    def read(self):
        ret = self._stdout.read(Encoder.FRAME_SIZE)
        if len(ret) != Encoder.FRAME_SIZE:
            return b''
        return ret
    def cleanup(self):
        proc = self._process
        if proc is None:
            return
        proc.kill()
        if proc.poll() is None:
            proc.communicate()

        self._process = None


class VoiceRecording(commands.Cog):    
    
    voice_packets = {}
    audio_files = {}
    transcription = []
    voice_channel = None
    bot : Bot = None
    daily_manual_joins = 0
    registered_users = []
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.join_conversation.start()
        self.last_join = datetime(2000, 1, 1)


    @app_commands.command(name="voice_chat", description="Manually force the bot to join your VC for a chat")
    async def force_join(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            if self.daily_manual_joins > MAX_JOIN_LIMIT:
                await interaction.followup.send("Already joined 3 times today, please wait a day.", ephemeral=True)
                return
                
            with open("data/voice_conversations.json", "r") as f:
                registered_users = json.load(f)["registered_users"]
            
            if interaction.user.id not in registered_users:
                await interaction.followup.send("You must be a voice registered user to perform this command. Please register first")
                return
            
            self.last_join = datetime.now()
            self.voice_channel = await interaction.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
            self.daily_manual_joins += 1
            
            for _ in range(0, 3):
                await self.listen_for(LISTEN_TIME)
                
                await self.transcribe_audio()
                response = await self.generate_response()
                await self.create_audio(response)
                self.voice_channel.stop_listening()
            
            await self.voice_channel.disconnect()
            await self.cleanup()
            self.voice_channel = None
            self.transcription = []
            
            await interaction.followup.delete()
        except:
            await interaction.followup.send('Encountered an error, try again later.', ephemeral=True)
        

    @tasks.loop(minutes=20)
    async def join_conversation(self):
        try:
            active_voice_channel = await self.get_active_vc()
            if await self.can_join(active_voice_channel):
                self.last_join = datetime.now()
                self.voice_channel = await active_voice_channel.connect(cls=voice_recv.VoiceRecvClient)
                
                for _ in range(0, random.randint(MIN_LISTENS, MAX_LISTENS)):
                    await self.listen_for(LISTEN_TIME)
                    
                    await self.transcribe_audio()
                    response = await self.generate_response()
                    await self.create_audio(response)
                    self.voice_channel.stop_listening()
                
                self.voice_channel.stop_listening()
                await self.voice_channel.disconnect()
                await self.cleanup()
                self.voice_channel = None
                self.transcription = []
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Encountered an error in joining conversation: {e}\n\n')
    
    
    async def can_join(self, active_voice_channel) -> bool:
        try:
            if active_voice_channel is None or self.voice_channel is not None:
                return False
            
            if random.random() >= JOIN_CHANCE:
                return False
            if (datetime.now() - self.last_join).total_seconds() < (COOLDOWN_TIME_HOURS * 3600):
                return False

            return True
        except:
            return False
        
        
    async def get_active_vc(self):
        try:
            with open('data/voice_conversations.json', "r") as f:
                registered_users = json.load(f)["registered_users"]
                
            for server in self.bot.bot.guilds:
                for channel in server.voice_channels:
                    enabled_users = [member for member in channel.members if member.id in registered_users]
                    if len(enabled_users) > 0:
                        return channel
            return None
        except:
            return None


    async def listen_for(self, t):
        with open('data/voice_conversations.json', 'r') as f:
            registered_users = json.load(f)["registered_users"]
            
        def save(user, data: voice_recv.VoiceData):
            if data.source.id in registered_users:
                self.voice_packets[data.source.display_name].append(data)
        
        for member in self.voice_channel.channel.members:
            self.voice_packets[member.display_name] = []
        self.voice_channel.listen(voice_recv.BasicSink(save))
        
        await asyncio.sleep(t)
    
    
    async def transcribe_audio(self):
        try:
            packets_to_process = self.voice_packets
            translator = str.maketrans('', '', string.punctuation)
            
            for member, packets in packets_to_process.items():
                self.voice_packets[member] = self.voice_packets[member][len(packets):]
                if len(packets) > 5:
                    cleaned_words = [word.translate(translator) for word in member.split()]
                    filename = ''.join(cleaned_words) + '.wav'
                    
                    with wave.open(filename, 'wb') as file:
                        file.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))
                        for data in packets:
                            file.writeframes(data.pcm)
                        self.audio_files[member] = filename
            
            for member, file in self.audio_files.items():
                with open(file, 'rb') as file:
                    self.transcription.append({member: openai.audio.transcriptions.create(
                        model="whisper-1",
                        file=file
                    ).text})
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Encountered an error when transcibing audio:\n{e}\n\n')
    
    
    async def cleanup(self):
        try:
            self.voice_packets = {}
            for file in self.audio_files.values():
                os.remove(file)
            self.audio_files = {}
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Encountered an error when cleaning up files:\n{e}\n\n')
    
    
    async def generate_response(self):
        try:
            instructions = self.bot.text.chat_prompt + INSTRUCTION_PROMPT
            messages = [{"role": "system", "content": instructions}]
            
            for audio in self.transcription:
                for member, text in audio.items():
                    if member != self.bot.name:
                        messages.append({"role": "user", "content": '{}: {}'.format(member, text)})
                    else:
                        messages.append({"role": "assistant", "content": text})
            
            response = openai.chat.completions.create(
                    model="gpt-4-0613",
                    messages=messages,
                    n=1,
                    stream=True
                )
            
            response_text = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    response_text += chunk.choices[0].delta.content
                    
            self.transcription.append({self.bot.name: response_text})
            
            return response_text
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Encountered an exception when generating a text response:\n{e}\n\n')


    async def create_audio(self, response):
        try:
            body = {'text': response,
                    'model_id': self.bot.voice.voice_model,
                    'voice_settings': {'stability': 0.15,
                                    'similarity_boost': 0.7,
                                    'style': 0.1,
                                    'use_speaker_boost': True
                                    }
                    }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url='https://api.elevenlabs.io/v1/text-to-speech/' + self.bot.voice.elevenlabs.voice['voice_id'] + '/stream?optimize_streaming_latency=4',
                                        headers={'XI-API-KEY': self.bot.voice.elevenlabs.api_key},
                                        json=body) as r:
                    content = io.BytesIO(await r.read())
                    self.voice_channel.play(StreamingAudio(content.read(), pipe=True))
            
            while self.voice_channel.is_playing():
                await asyncio.sleep(1)
                
        except Exception as e:
            with open('log.txt', 'a') as f:
                f.write(f'Encountered an exception when playing response:\n{e}\n\n')