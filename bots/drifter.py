import os
import json
from discord import app_commands
from dotenv import load_dotenv
from src.elevenlab import *
from src.bot import *


#? Initializations and global values


load_dotenv()
DRIFTER_TOKEN = os.getenv('DISCORD_TOKEN_DRIFTER')
DRIFTER_VOICE_KEY = os.getenv('ELEVEN_TOKEN_DRIFTER')

drifter = Bot(
    _name="Drifter",
    _discord_token=DRIFTER_TOKEN,
    _status_messages={
        'credits': 'Ooooh, you hate to see that one!',
        'reset': "Scanning bio-metrics, AHHHH I\'m just kiddin\', you know you\'re authorized!!",
        'chat': {'response': 'Good ol\' {USERNAME} decided to ask me: ',
                 'error': 'It happens. Well, head on back and take the gambit again.'},
        'speak': {'too_long': 'Brother, we don\'t have time for this. Those motes are needing banked!',
                  'error': 'Hey, don\'t feel too bad. The best thing about Gambit is it never ends. Look me up anytime.'}
        },
    _voice_name="The Drifter",
    _voice_key=DRIFTER_VOICE_KEY,
    _voice_model="eleven_multilingual_v2",
    _chat_prompt="""Roleplay as The Drifter from Destiny 2. Emulate his irreverent 
                    temperament, strange behaviors, and personality. Use his phrases 
                    such as "Brother" when referring to other Guardians. Focus on essential 
                    details, while omitting unnecessary ones. Respond to all prompts and 
                    questions, while keeping answers under 750 characters.""".replace("\n", " "),
    _use_voice=True,
    _use_text=True
)


#? Drifter Bot Commands


#* Setup initial things on server join
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Alright alright alright! Let\'s see what we got! {} on the field\'!".format(guild.name))
    await drifter.botInit()
    log.write(f'Drifter joined a new server: {guild.name}\n\n')
    log.close()

#* Calibration for starting of Drifter bot
@drifter.bot.event
async def on_ready():
    await drifter.on_ready()

#* Slash command for text-to-speech for Rhulk
@drifter.bot.tree.command(name="drifter_speak", description="Text-to-speech to have Drifter speak some text!")
@app_commands.describe(text="What should Drifter say?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.25",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.75")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.25, clarity: float=0.8, style: float=0.75):
    await drifter.voice.speak(interaction, text, stability, clarity, style)

#* Slash command for Drifter VC text-to-speech
@drifter.bot.tree.command(name="drifter_vc_speak", description="Text-to-speech to have Drifter speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Drifter say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.25",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.75")
async def drifter_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.25, clarity: float=0.8, style: float=0.75):
    await drifter.voice.vc_speak(interaction, text, vc, stability, clarity, style)

#* Slash command for showing remaining credits for text-to-speech
@drifter.bot.tree.command(name="drifter_credits", description="Shows the credits remaining for ElevenLabs for The Drifter")
async def drifter_credits(interaction: discord.Interaction):
    await drifter.voice.credits(interaction)

#* Slash command to get text prompt for Drifter
@drifter.bot.tree.command(name="drifter_prompt", description="Show the prompt that is used to prime the /drifter_chat command.")
async def drifter_prompt(interaction: discord.Interaction):
    await drifter.text.prompt(interaction)

#* Slash command for asking Drifter ChatGPT a question
@drifter.bot.tree.command(name="drifter_chat", description= "Ask Drifter anything you want!")
@app_commands.describe(prompt="What would you like to ask Drifter?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    await drifter.text.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

#* Reset the Drifter ChatGPT if it gets too out of hand.
@drifter.bot.tree.command(name="drifter_reset", description="Reset the /drifter_chat AI's memory in case he gets too far gone")
async def drifter_reset(interaction: discord.Interaction):
    await drifter.text.reset(interaction)

#* Shows the list of random topics to be used daily or with the /generate_conversation command
@drifter.bot.tree.command(name="drifter_topics", description="View the saved topics that the bots can chat over!")
async def topics(interaction: discord.Interaction):
    topics = json.load(open('data/topics.json'))
    response = ""
    for _, (key, value) in enumerate(topics.items()):
        response += f'**{key}:**\n'
        for v in value["topics"]:
            response += f'{v}\n'
        response += '\n'
    await interaction.response.send_message(f'Heh, listen to this brother. Those \'Disciples\' you killed are wanting to talk about these topics: \n\n{response}', ephemeral=True)

#* Add a topic to the topic list
@drifter.bot.tree.command(name="drifter_add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def drifter_add_topic(interaction: discord.Interaction, topic: str=None):
    if topic != None:
        topics = json.load(open('data/topics.json'))
        if topic not in topics['misc']["topics"]:
            topics['misc']["topics"].append(topic)
            with open('data/topics.json', 'w') as f:
                log = open('log.txt', 'a')
                f.write(json.dumps(topics, indent=4))
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                await interaction.response.send_message(f'Ooooh {interaction.user.global_name}! **{topic}** sounds like a fun thing to discuss!')
        else:
            await interaction.response.send_message(f'{interaction.user.global_name}, did that Primeval drain your Light? (Already in list)')
    else:
        await interaction.response.send_message(f'I\'ve been more entertained being cooped up down here than hearing that, {interaction.user.global_name}. (Must input something)')