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
from datetime import datetime
from discord.ext import voice_recv, commands, tasks

INSTRUCTION_PROMPT = ("You are in a Discord call with other members, and you will be provided "
                     "the different users as well as what they said in a 5 second timeframe. "
                     "The ordering of the sentences and users may not correspond with the actual "
                     "spoken order. Only respond with any input you may have, limiting your response to under 250 characters.")

MAX_LISTENS = 4
MIN_LISTENS = 2
LISTEN_TIME = 10
JOIN_CHANCE = 0.05
COOLDOWN_TIME_HOURS = 3

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
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.join_conversation.start()
        self.last_join = datetime(2000, 1, 1)


    @tasks.loop(minutes=15)
    async def join_conversation(self):
        try:
            active_voice_channel = await self.get_active_vc()
            if not await self.can_join(active_voice_channel):
                return
        except Exception as e:
            print(e)
        
        self.last_join = datetime.now()
        self.voice_channel = await active_voice_channel.connect(cls=voice_recv.VoiceRecvClient)
        
        for _ in range(0, random.randint(MIN_LISTENS, MAX_LISTENS)):
            await self.listen_for(LISTEN_TIME)
            self.voice_channel.stop_listening()
            
            await self.transcribe_audio()
            response = await self.generate_response()
            await self.create_audio(response)
        
        await self.voice_channel.disconnect()
        await self.cleanup()
        self.voice_channel = None
        self.transcription = []
    
    
    async def can_join(self, active_voice_channel) -> bool:
        if active_voice_channel is None or self.voice_channel is not None:
            return False
        
        if random.random() > JOIN_CHANCE:
            return False
        
        if (self.last_join - datetime.now()).total_seconds() < COOLDOWN_TIME_HOURS * 3600:
            return False

        return True
        
        
    async def get_active_vc(self) -> discord.VoiceChannel | None:
        with open('data/voice_conversations.json', "r") as f:
            registered_users = json.load(f)["registered_users"]
            
        for server in self.bot.bot.guilds:
            for channel in server.voice_channels:
                enabled_users = [member for member in channel.members if member.id in registered_users]
                if len(enabled_users) > 0:
                    return channel
        return None


    async def listen_for(self, t):
        def save(user, data: voice_recv.VoiceData):
            self.voice_packets[data.source.display_name].append(data)
        
        for member in self.voice_channel.channel.members:
            self.voice_packets[member.display_name] = []
        self.voice_channel.listen(voice_recv.BasicSink(save))
        
        await asyncio.sleep(t)
    
    
    async def transcribe_audio(self):
        
        packets_to_process = self.voice_packets
        translator = str.maketrans('', '', string.punctuation)
        
        for member, packets in packets_to_process.items():
            if len(packets) > 0:
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
    
    
    async def cleanup(self):
        self.voice_packets = {}
        for file in self.audio_files.values():
            os.remove(file)
        self.audio_files = {}
    
    
    async def generate_response(self):
        instructions = self.bot.text.chat_prompt + INSTRUCTION_PROMPT
        messages = [{"role": "system", "content": instructions}]
        
        for audio in self.transcription:
            for member, text in audio.items():
                if member != self.bot.name:
                    messages.append({"role": "user", "content": '{}: {}'.format(member, text)})
                else:
                    messages.append({"role": "assistant", "content": text})
        
        print(messages)
        
        response = openai.chat.completions.create(
                model="gpt-4-0613",
                messages=messages,
                n=1
            ).choices[0].message.content
        
        self.transcription.append({self.bot.name: response})
        
        return response


    async def create_audio(self, response):
        
        try:
            body = {'text': response,
                    'model_id': self.bot.voice.voice_model,
                    'voice_settings': {'stability': 0.2,
                                    'similarity_boost': 0.7,
                                    'style': 0.1,
                                    'use_speaker_boost': True
                                    }
                    }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url='https://api.elevenlabs.io/v1/text-to-speech/' + self.bot.voice.elevenlabs.voice['voice_id'] + '/stream?optimize_streaming_latency=2',
                                        headers={'XI-API-KEY': self.bot.voice.elevenlabs.api_key},
                                        json=body) as r:
                    content = io.BytesIO(await r.read())
                    self.voice_channel.play(StreamingAudio(content.read(), pipe=True))
            
            while self.voice_channel.is_playing():
                await asyncio.sleep(1.5)
                
        except Exception as e:
            print(f'Found an exception: {e}')