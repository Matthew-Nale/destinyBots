import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from src.bot import Bot

#? Initializations and global values

load_dotenv()
CALUS_TOKEN = os.getenv('DISCORD_TOKEN_CALUS')
CALUS_VOICE_KEY = os.getenv('ELEVEN_TOKEN_CALUS')

calus = Bot(
    _name='Calus', 
    _discord_token=CALUS_TOKEN, 
    _status_messages = {
        'credits': 'When the end comes, I reserve the right to be the last.',
        'reset': 'Ah {USERNAME}, my favorite Guardian! Come, let us enjoy ourselves!',
        'chat': {'response': '{USERNAME} has asked your generous Emperor of the Cabal: ',
                 'error' : 'My Shadow... what has gotten into you?'},
        'speak': {'too_long': 'My Shadow, we do not have time before the end of all things to do this.',
                  'error': 'Arghhh, Cemaili!'}
        },
    _voice_name="Calus, Emperor of the Cabal",
    _voice_key=CALUS_VOICE_KEY, 
    _voice_model="eleven_english_v2",
    _chat_prompt="""Roleplay as Calus, the Cabal Emperor from Destiny 2. Emulate his hedonistic,
                    narcissistic, and adoration personality. Use phrases like 'My Shadow' and occasional laughter when
                    relevant. Focus on essential details, omitting unnecessary ones about Darkness and Light. Respond
                    to all prompts and questions, while keeping answers under 1000 characters""".replace("\n", " "),
    _use_voice=True,
    _use_text=True
)

#? Calus Bot Commands

@calus.bot.event
async def on_guild_join(guild: discord.Guild) -> (None):
    """
    Sends entrance message to guild on join

    :param guild (discord.Guild): Server that bot has joined
    """
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Ah. Finally found you. You busy little Lights.")
    await calus.botInit()
    log.write(f'Calus joined a new server: {guild.name}.\n\n')
    log.close()

@calus.bot.event
async def on_ready():
    await calus.on_ready()

@calus.bot.tree.command(name="calus_speak", description="Text-to-speech to have Calus speak some text!")
@app_commands.describe(text="What should Calus say?",
                       stability="How stable should Calus sound? Range is 0:1.0, default 0.3",
                       clarity="How similar to the in-game voice should it be? Range is 0:1.0, default 0.65",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.45")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.3, clarity: float=0.65, style: float=0.45):
    await calus.voice.speak(interaction, text, stability, clarity, style)
    
@calus.bot.tree.command(name="calus_vc_speak", description="Text-to-speech to have Calus speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Calus say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.3.",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.65",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.45")
async def calus_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.3, clarity: float=0.65, style: float=0.45):
    await calus.voice.vc_speak(interaction, text, vc, stability, clarity, style)

@calus.bot.tree.command(name="calus_credits", description="Shows the credits remaining for ElevenLabs for Emperor Calus")
async def calus_credits(interaction: discord.Interaction):
    await calus.voice.credits(interaction)

@calus.bot.tree.command(name="calus_prompt", description="Show the prompt that is used to prime the /calus_chat command.")
async def calus_prompt(interaction: discord.Interaction):
    await calus.text.prompt(interaction)

@calus.bot.tree.command(name="calus_chat", description= "Ask Calus anything you want!")
@app_commands.describe(prompt="What would you like to ask Calus?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.75.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.0.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.75, presence_penalty: float=0.0):
    await calus.text.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

@calus.bot.tree.command(name="calus_reset", description="Reset the /calus_chat AI's memory in case he gets too far gone")
async def calus_reset(interaction: discord.Interaction):
    await calus.text.reset(interaction)