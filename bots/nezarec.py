import os
import json
from discord import app_commands
from dotenv import load_dotenv
from src.elevenlab import *
from src.bot import *


#? Initializations and global values


load_dotenv()
NEZAREC_TOKEN = os.getenv('DISCORD_TOKEN_NEZAREC')

nezarec = Bot(
    _name="Nezarec",
    _discord_token=NEZAREC_TOKEN,
    _status_messages={
        'reset': 'This prison in-between… it will shatter. But I need power…',
        'chat': {'response': 'Ohh good... {USERNAME} decided to ask me: ',
                 'error': 'It\'s a shame we can\'t entertain our conversation further...'}
        },
    _chat_prompt="""Roleplay as  Nezarec, the Final God of Pain from Destiny 2 and
                    Disciple of the Witness. Emulate his hunger for pain and suffering, 
                    utter derangement, insanity, and sadistic tendencies. Focus on 
                    essential details, while omitting unnecessary ones. Respond to all 
                    prompts and questions, while keeping answers under 750 characters.""".replace("\n", " "),
    _use_voice=False,
    _use_text=True
)


#? Nezarec Bot Commands


#* Setup initial things on server join
@nezarec.bot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Guardians! Do not think you can escape me in {}!".format(guild.name))
    await nezarec.botInit()
    log.write(f'Nezarec joined a new server: {guild.name}\n\n')
    log.close()

#* Calibration for starting of Nezarec bot
@nezarec.bot.event
async def on_ready():
    await nezarec.on_ready()

#* Slash command to get text prompt for Nezarec
@nezarec.bot.tree.command(name="nezarec_prompt", description="Show the prompt that is used to prime the /nezarec_chat command.")
async def nezarec_prompt(interaction: discord.Interaction):
    await nezarec.text.prompt(interaction)

#* Slash command for asking Nezarec ChatGPT a question
@nezarec.bot.tree.command(name="nezarec_chat", description= "Ask Nezarec anything you want!")
@app_commands.describe(prompt="What would you like to ask Nezarec?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    await nezarec.text.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

#* Reset the Rhulk ChatGPT if it gets too out of hand.
@nezarec.bot.tree.command(name="nezarec_reset", description="Reset the /chat_nezarec AI's memory in case he gets too far gone")
async def nezarec_reset(interaction: discord.Interaction):
    await nezarec.text.reset(interaction)