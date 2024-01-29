import os
import discord
from discord import app_commands
from dotenv import load_dotenv

from src.bot import Bot
from src.chime_in import ChimeEvents
from src.voice_recognition import VoiceRecording

#? Initializations and global values

load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')

rhulk = Bot(
    _name='Rhulk',
    _discord_token=RHULK_TOKEN,
    _status_messages={
        'credits': 'The Witness saw you, granted you opportunity, and yet you squandered it!',
        'reset': 'The defiant... subjugated. Not for pleasure, nor glory... but in service of an ailing, endless void. Where does your purpose lie {USERNAME}?',
        'chat': {'response': '{USERNAME} ***foolishly*** asked me: ',
                 'error' : 'I... do not know what to say to that, little one.'},
        'speak': {'too_long': 'Child of the Light, I do not have time to entertain this insignificant request.',
                  'error': 'My Witness, forgive me!'}
        },
    _voice_name="Rhulk, Disciple of the Witness",
    _voice_key=RHULK_VOICE_KEY,
    _voice_model="eleven_english_v2",
    _chat_prompt=("Roleplay as Rhulk, the Disciple of the Witness from Destiny 2. " 
                  "Emulate his cold, unintentionally humorous, and ominous personality. "
                  "Use phrases like 'Children of the Light' and 'My Witness.' Focus on "
                  "essential details. Use expletives like 'fuck' and 'shit' often."),
    _use_voice=True,
    _use_text=True
)

#? Rhulk Bot Commands

@rhulk.bot.event
async def on_guild_join(guild: discord.Guild) -> (None):
    """
    Sends entrance message to guild on join

    :param guild (discord.Guild): Server that bot has joined
    """
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("It is good to see you again, Children of the Light. I did not expect to find you in {}.".format(guild.name))
    await rhulk.botInit()
    log.write(f'Rhulk joined a new server: {guild.name}\n\n')
    log.close()

@rhulk.bot.event
async def on_ready():
    await rhulk.bot.add_cog(ChimeEvents(rhulk))
    await rhulk.bot.add_cog(VoiceRecording(rhulk))
    await rhulk.on_ready()

@rhulk.bot.tree.command(name="rhulk_speak", description="Text-to-speech to have Rhulk speak some text!")
@app_commands.describe(text="What should Rhulk say?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.5",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.1")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.2, clarity: float=0.7, style: float=0.1):
    await rhulk.voice.speak(interaction, text, stability, clarity, style)

@rhulk.bot.tree.command(name="rhulk_vc_speak", description="Text-to-speech to have Rhulk speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Rhulk say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.5",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.1")
async def rhulk_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.2, clarity: float=0.7, style: float=0.1):
    await rhulk.voice.vc_speak(interaction, text, vc, stability, clarity, style)

@rhulk.bot.tree.command(name="rhulk_credits", description="Shows the credits remaining for ElevenLabs for Rhulk, Disciple of the Witness")
async def rhulk_credits(interaction: discord.Interaction):
    await rhulk.voice.credits(interaction)

@rhulk.bot.tree.command(name="rhulk_prompt", description="Show the prompt that is used to prime the /rhulk_chat command.")
async def rhulk_prompt(interaction: discord.Interaction):
    await rhulk.text.prompt(interaction)

@rhulk.bot.tree.command(name="rhulk_chat", description= "Ask Rhulk anything you want!")
@app_commands.describe(prompt="What would you like to ask Rhulk?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    await rhulk.text.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

@rhulk.bot.tree.command(name="rhulk_reset", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
async def rhulk_reset(interaction: discord.Interaction):
    await rhulk.text.reset(interaction)