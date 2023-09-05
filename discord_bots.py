import os
import discord
import openai
import asyncio
import random
import pytz
from datetime import datetime
from discord import app_commands
from discord.utils import get
from discord.ext import tasks
from dotenv import load_dotenv
from elevenlab import *
from bot import *

#? Initializations and global values

#* Load and set env variables for API calls
load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
CALUS_TOKEN = os.getenv('DISCORD_TOKEN_CALUS')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')
CALUS_VOICE_KEY = os.getenv('ELEVEN_TOKEN_CALUS')

#* Setup Bot with classes
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

calus = Bot('Calus', CALUS_TOKEN, "Calus, Emperor of the Cabal", CALUS_VOICE_KEY, 
            """Roleplay as Calus, the Cabal Emperor from Destiny 2. Emulate his hedonistic,
            narcissistic, and adoration personality. Use phrases like 'My Shadow' and occasional laughter when
            relevant. Focus on essential details, omitting unnecessary ones about Darkness and Light. Respond
            to all prompts and questions, while keeping answers under 1000 characters""".replace("\n", " "),
            {'credits': 'When the end comes, I reserve the right to be the last.',
             'reset': 'Ah {USERNAME}, my favorite Guardian! Come, let us enjoy ourselves!',
             'chat': {'response': '{USERNAME} has asked your generous Emperor of the Cabal: ',
                      'error' : 'My Shadow... what has gotten into you?'},
             'speak': {'too_long': 'My Shadow, we do not have time before the end of all things to do this.',
                       'error': 'Arghhh, Cemaili!'}
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
async def speak(interaction: discord.Interaction, text: str, stability: float=0.5, clarity: float=0.8, style: float=0.1):
    await rhulk.speak(interaction, text, stability, clarity, style)

#* Slash command for Rhulk VC text-to-speech
@rhulk.bot.tree.command(name="rhulk_vc_speak", description="Text-to-speech to have Rhulk speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Rhulk say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.5",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.8",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.1")
async def rhulk_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.5, clarity: float=0.8, style: float=0.1):
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
                       temperature="How random should the response be? Range between 0.0:2.0, default is 0.8.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=0.8, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    rhulk.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

#* Reset the Rhulk ChatGPT if it gets too out of hand.
@rhulk.bot.tree.command(name="rhulk_reset", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
async def rhulk_reset(interaction: discord.Interaction):
    await rhulk.reset(interaction)

#* Shows the list of random topics to be used daily or with the /generate_conversation command
@rhulk.bot.tree.command(name="rhulk_topics", description="View the saved topics that Rhulk and Calus can chat over!")
async def topics(interaction: discord.Interaction):
    topics = open('topics.txt').readlines()
    response = ""
    for topic in topics:
        response += topic
    await interaction.response.send_message(f'You wish to know the conversation topics for the Witness\'s Disciples? Very well, here is what we may discuss: \n**{response}**')

#* Add a topic to the topic list
@rhulk.bot.tree.command(name="rhulk_add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def rhulk_add_topic(interaction: discord.Interaction, topic: str):
    if topic != None:
        with open('topics.txt', 'r') as f:
            topics_list = f.read().splitlines()
            if topic not in topics_list:
                log = open('log.txt', 'a')
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                with open('topics.txt', 'a') as r:
                    r.write(topic)
                    r.write('\n')
                await interaction.response.send_message(f'Ahhhh {interaction.user.global_name}, *{topic}* does sound interesting, does it not?')
            else:
                await interaction.response.send_message(f'{interaction.user.global_name}, we have already discussed that matter earlier. Were you not paying attention? (Already in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}, please do not bore me with that pitiful topic. (Must input something)')
    
#* Remove a topic from the topic list
@rhulk.bot.tree.command(name="rhulk_remove_topic", description="Remove a topic from the topic list.")
@app_commands.describe(topic="What topic should be removed from the list?")
async def rhulk_remove_topic(interaction: discord.Interaction, topic: str):
    if topic != None:
        with open('topics.txt', 'r') as f:
            topics_list = f.read().splitlines()
            print(topics_list)
            if topic in topics_list:
                log = open('log.txt', 'a')
                log.write(f'Removing a topic from the list: {topic}\n\n')
                log.close()
                topics_list.remove(topic)
                with open('topics.txt', 'w') as r:
                    for t in topics_list:
                        r.write(t + '\n')
                await interaction.response.send_message(f'Fine, {interaction.user.global_name}, I will not bring {topic} up again. For now.')
            else:
                await interaction.response.send_message(f'{interaction.user.global_name}, we never have discussed that... (Not in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}, why would we ever discuss that? (Must input something)')

#* Manually generate a random or specific conversation with Rhulk being the first speaker
@rhulk.bot.tree.command(name="rhulk_start_conversation", description="Have Rhulk start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.")
async def rhulk_start_conversation(interaction: discord.Interaction, topic: str=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        convo, chosen_topic = generate_random_conversation('Rhulk', topic)
        await interaction.followup.send(f'*{interaction.user.display_name} wanted to hear Calus and I\'s conversation about {chosen_topic}. Here is how it unfolded:*')
        for line in convo:
            if 'Rhulk' in line:
                await rhulk.bot.get_channel(interaction.channel_id).send(line['Rhulk'])
                await asyncio.sleep(7.5)
            elif 'Calus' in line:
                await calus.bot.get_channel(interaction.channel_id).send(line['Calus'])
                await asyncio.sleep(7.5)
        
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Rhulk: ' + e + '\n\n')
        await interaction.followup.send('Hmmm, I do not quite remember how the conversation went. (Bug Radiolorian for future fixes)')
    log.close()

#? Calus Bot Commands

#* Send message to "general" on join
@calus.bot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Ah. Finally found you. You busy little Lights.")
    await calus.botInit()
    log.write(f'Calus joined a new server: {guild.name}.\n\n')
    log.close()

#* Calibration for starting of Calus bot
@calus.bot.event
async def on_ready():
    await calus.on_ready()

#* Slash command for text-to-speech for Calus
@calus.bot.tree.command(name="calus_speak", description="Text-to-speech to have Calus speak some text!")
@app_commands.describe(text="What should Calus say?",
                       stability="How stable should Calus sound? Range is 0:1.0, default 0.3",
                       clarity="How similar to the in-game voice should it be? Range is 0:1.0, default 0.65",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.45")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.3, clarity: float=0.65, style: float=0.45):
    await calus.speak(interaction, text, stability, clarity, style)
    
#* Slash command for Calus VC text-to-speech
@calus.bot.tree.command(name="calus_vc_speak", description="Text-to-speech to have Calus speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Calus say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.3.",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.65",
                       style="(Optional) How exaggerated should the text be read? Float from 0-1.0, default is 0.45")
async def calus_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.3, clarity: float=0.65, style: float=0.45):
    await calus.vc_speak(interaction, text, vc, stability, clarity, style)

#* Slash command for showing remaining credits for text-to-speech for Calus
@calus.bot.tree.command(name="calus_credits", description="Shows the credits remaining for ElevenLabs for Emperor Calus")
async def calus_credits(interaction: discord.Interaction):
    await calus.credits(interaction)

#* Calus slash command to get text prompt
@calus.bot.tree.command(name="calus_prompt", description="Show the prompt that is used to prime the /calus_chat command.")
async def calus_prompt(interaction: discord.Interaction):
    await calus.prompt(interaction)

#* Calus slash command for asking Calus ChatGPT a question
@calus.bot.tree.command(name="calus_chat", description= "Ask Calus anything you want!")
@app_commands.describe(prompt="What would you like to ask Calus?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.75.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.0.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.75, presence_penalty: float=0.0):
    await calus.chat(interaction, prompt, temperature, frequency_penalty, presence_penalty)

#* Reset the Calus ChatGPT if it gets too out of hand.
@calus.bot.tree.command(name="calus_reset", description="Reset the /calus_chat AI's memory in case he gets too far gone")
async def calus_reset(interaction: discord.Interaction):
    await calus.reset(interaction)

#* Shows the list of random topics to be used daily or with the /generate_conversation command
@calus.bot.tree.command(name="calus_topics", description="View the saved topics that Rhulk and Calus can chat over!")
async def topics(interaction: discord.Interaction):
    topics = open('topics.txt').readlines()
    response = ""
    for topic in topics:
        response += topic
    await interaction.response.send_message(f'*(laughter)* {interaction.user.global_name}, my favorite Guardian! Here is what I was thinking of asking Rhulk: \n**{response}**')

#* Add a topic to the topic list
@calus.bot.tree.command(name="calus_add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def calus_add_topic(interaction: discord.Interaction, topic: str):
    if topic != None:
        with open('topics.txt', 'r') as f:
            topics_list = f.read().splitlines()
            if topic not in topics_list:
                log = open('log.txt', 'a')
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                with open('topics.txt', 'a') as r:
                    r.write(topic)
                    r.write('\n')
                await interaction.response.send_message(f'Ohhh {interaction.user.global_name}! *{topic}* would make a fine topic!')
            else:
                await interaction.response.send_message(f'{interaction.user.global_name}, why not think of a more... amusing topic? (Already in list)')
    else:
        await interaction.response.send_message(f'Hmmm {interaction.user.global_name}. I truly wish you would see more joy in this. (Must input something)')

#* Remove a topic from the topic list
@calus.bot.tree.command(name="calus_remove_topic", description="Remove a topic from the topic list.")
@app_commands.describe(topic="What topic should be removed from the list?")
async def calus_remove_topic(interaction: discord.Interaction, topic: str):
    if topic != None:
        with open('topics.txt', 'r') as f:
            topics_list = f.read().splitlines()
            print(topics_list)
            if topic in topics_list:
                log = open('log.txt', 'a')
                log.write(f'Removing a topic from the list: {topic}\n\n')
                log.close()
                topics_list.remove(topic)
                with open('topics.txt', 'w') as r:
                    for t in topics_list:
                        r.write(t + '\n')
                await interaction.response.send_message(f'Oh {interaction.user.global_name}, *{topic}* is such a fine topic though! But if you insist...')
            else:
                await interaction.response.send_message(f'Why, I have never even thought of that {interaction.user.global_name}! (Not in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}, why bother worrying about these petty topics? (Must input something)')

#* Manually generate a random or specific conversation with Rhulk being the first speaker
@calus.bot.tree.command(name="calus_start_conversation", description="Have Calus start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.")
async def calus_start_conversation(interaction: discord.Interaction, topic: str=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        convo, chosen_topic = generate_random_conversation('Calus', topic)
        await interaction.followup.send(f'*{interaction.user.display_name}, my most loyal Shadow, asked Rhulk and I to talk about {chosen_topic}! Here is how that went:*')
        for line in convo:
            if 'Rhulk' in line:
                await rhulk.bot.get_channel(interaction.channel_id).send(line['Rhulk'])
                await asyncio.sleep(7.5)
            elif 'Calus' in line:
                await calus.bot.get_channel(interaction.channel_id).send(line['Calus'])
                await asyncio.sleep(7.5)
        
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Calus: ' + e + '\n\n')
        await interaction.followup.send('Hmmm, I do not quite remember how the conversation went. (Bug Radiolorian for future fixes)')
    log.close()

#? Random Conversation Generation

#* Generating the new random conversation
def generate_random_conversation(first_speaker="Rhulk", topic=None):
    log = open('log.txt', 'a')
    try:
        if topic == None:
            topics = open('topics.txt').read().splitlines()
            chosen_topic = topics[random.randint(0, len(topics) - 1)]
        else:
            chosen_topic = topic
        
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=[{'role':'system', 'content':"""Create dialogue: Rhulk and Emperor Calus, Disciples of the Witness 
                       in Destiny 2. Rhulk cold to Calus, while Calus is super joyful and laughs often. Rhulk extremely loyal 
                       First Disciple of the Witness, last of his species; Calus, self proclaimed Cabal Emperor, new
                       and unconventional Disciple, indifferent to Witness's plans. Topic: {}. Rhulk's egotistical, 
                       mocking, prideful; Calus's confident, amused, joyful. Stay in character and on topic. Use emotions in text. Be 
                       extremely entertaining and creative. Format: Rhulk: TEXT, Calus: TEXT. Limit to under 500 characters. {} starts.""".format(chosen_topic, first_speaker)
            }],
            n=1
        )
        
        convo = (completion.choices[0].message.content).splitlines()
        while "" in convo:
            convo.remove("")
        
        formatted_convo = []
        for line in convo:
            if "Rhulk: " in line:
                formatted_convo.append({'Rhulk': line.split(': ', 1)[1]})
            elif "Calus: " in line:
                formatted_convo.append({'Calus': line.split(': ', 1)[1]})
        
        log.write(f'Generated a conversation with the topic: {chosen_topic}: \n{formatted_convo}\n\n')
        log.close()
        return formatted_convo, chosen_topic
    except Exception as e:
        log.write('Encountered an error when generating a conversation: ' + e + '\n\n')
        log.close()
        return e

#* Creating a new conversation at 1pm EST everyday
@tasks.loop(seconds = 45)
async def scheduledBotConversation():
    print('test')
    now = datetime.now(pytz.timezone('US/Eastern'))
    if now.hour == 13 and now.minute == 0:
        log = open('log.txt', 'a')
        try:
            if random.randint(0, 1) == 0:
                first_speaker = 'Rhulk'
            else:
                first_speaker = 'Calus'
                
            for guild in rhulk.bot.guilds:
                if guild.name == "Victor's Little Pogchamps":
                    channel_id = get(guild.channels, name="rhulky-whulky").id
                    break
            
            convo, _ = generate_random_conversation(first_speaker)
            
            for line in convo:
                if 'Rhulk' in line:
                    await rhulk.bot.get_channel(channel_id).send(line['Rhulk'])
                    await asyncio.sleep(7.5)
                elif 'Calus' in line:
                    await calus.bot.get_channel(channel_id).send(line['Calus'])
                    await asyncio.sleep(7.5)
            log.write('Finished random conversation topic as scheduled.\n\n')
        except Exception as e:
            log.write('Encountered an error in the Random Conversation Generation: ' + e + '\n\n')
        log.close()

#? Running bots

async def main():
    #* Create log.txt and provide date of creation
    log = open("log.txt", "w")
    log.write(f'Started bots at {datetime.now()}\n\n')
    log.close()


    #* Run bots until manually quit
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop = await asyncio.gather(
        calus.bot.start(calus.discord_token),
        rhulk.bot.start(rhulk.discord_token),
        scheduledBotConversation.start(),
    )

asyncio.run(main())