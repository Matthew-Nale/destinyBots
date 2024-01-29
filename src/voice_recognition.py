import discord
import os
import wave
import string
import openai
import asyncio
import io

from elevenlabs import generate
from src.bot import Bot
from discord import app_commands
from discord.ext import voice_recv, commands

INSTRUCTION_PROMPT = ("You are in a Discord call with other members, and you will be provided "
                     "the different users as well as what they said in a 5 second timeframe. "
                     "The ordering of the sentences and users may not correspond with the actual "
                     "spoken order. Only respond with any input you may have, limiting your response to under 250 characters.")

class VoiceRecording(commands.Cog):    
    
    voice_packets = {}
    audio_files = {}
    transcription = {}
    voice_channel = None
    
    
    def __init__(self, bot: Bot):
        self.bot = bot


    @app_commands.command(name="start")
    async def start(self, ctx: discord.Interaction):
        def callback(user, data: voice_recv.VoiceData):
            self.voice_packets[data.source.display_name].append(data)
        
        self.voice_channel = await ctx.user.voice.channel.connect(cls=voice_recv.VoiceRecvClient)
        
        for member in self.voice_channel.channel.members:
            self.voice_packets[member.display_name] = []
            
        self.voice_channel.listen(voice_recv.BasicSink(callback))


    @app_commands.command(name="stop")
    async def stop(self, ctx: discord.Interaction):
        await self.save_audio()
        await self.transcribe_audio()
        
        response = await self.generate_response()
        await self.create_audio(response)
        
        while self.voice_channel.is_playing():
            await asyncio.sleep(1.5)
        
        await self.cleanup()
        await ctx.guild.voice_client.disconnect()
    

    async def save_audio(self):
        translator = str.maketrans('', '', string.punctuation)
        
        for member, packets in self.voice_packets.items():
            if len(packets) > 0:
                cleaned_words = [word.translate(translator) for word in member.split()]
                filename = ''.join(cleaned_words) + '.wav'
                
                with wave.open(filename, 'wb') as file:
                    file.setparams((2, 2, 44100, 0, 'NONE', 'NONE'))
                    for data in packets:
                        file.writeframes(data.pcm)
                    self.audio_files[member] = filename
    
    
    async def transcribe_audio(self):
        for member, file in self.audio_files.items():
            with open(file, 'rb') as file:
                self.transcription[member] = openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=file
                ).text
    
    
    async def cleanup(self):
        self.voice_packets = {}
        for file in self.audio_files.values():
            os.remove(file)
        self.audio_files = {}
    
    
    async def generate_response(self):
        instructions = self.bot.text.chat_prompt + INSTRUCTION_PROMPT
        messages = [{"role": "system", "content": instructions}]
        
        for user, text in self.transcription.items():
            messages.append({"role": "user", "content": '{}: {}'.format(user, text)})
        
        print(messages)
        
        response = openai.chat.completions.create(
                model="gpt-4-0613",
                messages=messages,
                n=1
            )
        
        return response.choices[0].message.content

    async def create_audio(self, response):
        
        response_file = 'response.mp3'
        
        try:
            
            audio_stream = generate(
                text=response,
                api_key=self.bot.voice.elevenlabs.api_key,
                voice=self.bot.voice.elevenlabs.voice['voice_id'],
                model=self.bot.voice.voice_model,
                stream=True,
                stream_chunk_size=1024,
                latency=3)
            
            with open(response_file, 'wb') as f:
                for chunk in audio_stream:
                    if chunk is not None:
                        f.write(chunk)
            
            self.voice_channel.play(discord.FFmpegPCMAudio(source=response_file))
        except Exception as e:
            print(f'Encountered an Exception: {e}')
    
        self.audio_files[self.bot.name] = response_file
    