import discord
import openai
import asyncio
import random
import pytz
import json
from datetime import datetime
from discord import app_commands
from discord.utils import get
from discord.ext import tasks
from src.bot import CHAT_MODEL
from bots.rhulk import rhulk
from bots.calus import calus

#? Random Conversation Generation

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

#* Manually generate a random or specific conversation with Calus being the first speaker
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

#* Generating the new random conversation
def generate_random_conversation(first_speaker="Rhulk", topic=None):
    log = open('log.txt', 'a')
    try:
        if topic == None:
            topics = json.load(open('topics.json'))
            weights = {'discord_members': 5, 'insult': 1, 'discussion': 1, 'misc': 1}
            chosen_key = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            chosen_topic = topics[chosen_key][random.randint(0, len(topics[chosen_key]) - 1)]
        else:
            chosen_topic = topic
        
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=[{'role':'system', 'content':"""Create dialogue: Characters: Rhulk and Emperor Calus, Disciples of the Witness 
                       in Destiny 2. Rhulk annoyed with Calus; Calus joyful and laughs often. Rhulk: extremely loyal, First Disciple 
                       of the Witness, last of the ancient Lubraean. Calus: former Emperor of the Cabal, new and unconventional Disciple, 
                       indifferent to Witness's plans. Topic: {}. Rhulk's egotistical, mocking, prideful; Calus's confident, amused, 
                       joyful. Stay in character and on provided topic. Be extremely entertaining and creative. Format: Rhulk: TEXT, 
                       Calus: TEXT. Limit to under 10 total lines of dialogue. {} starts.""".format(chosen_topic, first_speaker)
            }],
            n=1,
            temperature=1.2,
            frequency_penalty=0.3
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