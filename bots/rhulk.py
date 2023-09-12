import os
import json
from discord import app_commands
from dotenv import load_dotenv
from src.elevenlab import *
from src.bot import *

#? Initializations and global values

load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')

#* Setup Bot
rhulk = Bot('Rhulk', RHULK_TOKEN, "Rhulk, Disciple of the Witness", RHULK_VOICE_KEY,
            """Roleplay as Rhulk, the Disciple of the Witness from Destiny 2 and 
            antagonist to the Light and Guardians. Emulate his personality, use phrases 
            like "Children of the Light" and "My Witness." Focus on essential details, avoid 
            unnecessary information about Darkness and Light unless essential. Respond to all user 
            prompts and questions, while keeping responses under 1000 characters""".replace("\n", " "),
            {'credits': 'The Witness saw you, granted you opportunity, and yet you squandered it!',
             'reset': 'The defiant... subjugated. Not for pleasure, nor glory... but in service of an ailing, endless void. Where does your purpose lie {USERNAME}?',
             'chat': {'response': '{USERNAME} ***foolishly*** asked me: ',
                      'error' : 'I... do not know what to say to that, little one.'},
             'speak': {'too_long': 'Child of the Light, I do not have time to entertain this insignificant request.',
                       'error': 'My Witness, forgive me!'}
             })

#? Rhulk Bot Commands

#* Setup initial things on server join
@rhulk.bot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("It is good to see you again, Children of the Light. I did not expect to find you in {}.".format(guild.name))
    await rhulk.botInit()
    log.write(f'Rhulk joined a new server: {guild.name}\n\n')
    log.close()

#* Calibration for starting of Rhulk bot
@rhulk.bot.event
async def on_ready():
    await rhulk.on_ready()

#* Slash command for text-to-speech for Rhulk
@rhulk.bot.tree.command(name="rhulk_speak", description="Text-to-speech to have Rhulk speak some text!")
@app_commands.describe(text="What should Rhulk say?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.5",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.1")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.2, clarity: float=0.7, style: float=0.1):
    await rhulk.speak(interaction, text, stability, clarity, style)

#* Slash command for Rhulk VC text-to-speech
@rhulk.bot.tree.command(name="rhulk_vc_speak", description="Text-to-speech to have Rhulk speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Rhulk say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.5",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.1")
async def rhulk_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.2, clarity: float=0.7, style: float=0.1):
    await rhulk.vc_speak(interaction, text, vc, stability, clarity, style)

#* Slash command for showing remaining credits for text-to-speech
@rhulk.bot.tree.command(name="rhulk_credits", description="Shows the credits remaining for ElevenLabs for Rhulk, Disciple of the Witness")
async def rhulk_credits(interaction: discord.Interaction):
    await rhulk.credits(interaction)

#* Slash command to get text prompt for Rhulk
@rhulk.bot.tree.command(name="rhulk_prompt", description="Show the prompt that is used to prime the /rhulk_chat command.")
async def rhulk_prompt(interaction: discord.Interaction):
    await rhulk.prompt(interaction)

#* Slash command for asking Rhulk ChatGPT a question
@rhulk.bot.tree.command(name="rhulk_chat", description= "Ask Rhulk anything you want!")
@app_commands.describe(prompt="What would you like to ask Rhulk?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    rhulk.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

#* Reset the Rhulk ChatGPT if it gets too out of hand.
@rhulk.bot.tree.command(name="rhulk_reset", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
async def rhulk_reset(interaction: discord.Interaction):
    await rhulk.reset(interaction)

#* Shows the list of random topics to be used daily or with the /generate_conversation command
@rhulk.bot.tree.command(name="rhulk_topics", description="View the saved topics that Rhulk and Calus can chat over!")
async def topics(interaction: discord.Interaction):
    topics = json.load(open('topics.json'))
    response = ""
    for _, (key, value) in enumerate(topics.items()):
        response += f'**{key}:**\n'
        for v in value["topics"]:
            response += f'{v}\n'
        response += '\n'
    await interaction.response.send_message(f'You wish to know the conversation topics for the Witness\'s Disciples? Very well, here is what we may discuss: \n\n{response}', ephemeral=True)

#* Add a topic to the topic list
@rhulk.bot.tree.command(name="rhulk_add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def rhulk_add_topic(interaction: discord.Interaction, topic: str):
    if topic != None:
        topics = json.load(open('topics.json'))
        if topic not in topics['misc']["topics"]:
            topics['misc']["topics"].append(topic)
            with open('topics.json', 'w') as f:
                log = open('log.txt', 'a')
                f.write(json.dumps(topics, indent=4))
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                await interaction.response.send_message(f'Ahhhh {interaction.user.global_name}, **{topic}** does sound interesting, does it not?')
        else:
            await interaction.response.send_message(f'{interaction.user.global_name}, we have already discussed that matter earlier. Were you not paying attention? (Already in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}, please do not bore me with that pitiful topic. (Must input something)')