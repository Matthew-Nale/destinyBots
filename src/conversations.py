import discord
import asyncio
import random
import pytz
import openai
import json
from datetime import datetime
from discord import app_commands
from discord.utils import get
from discord.ext import tasks
from src.bot import CHAT_MODEL
from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter
from bots.nezarec import nezarec


#? Conversation Generation

#* Sends messages from generated response
async def send_messages(conversation, channel):
    for line in conversation:
        if 'Rhulk' in line:
            async with rhulk.bot.get_channel(channel).typing():
                await asyncio.sleep(0.05 * len(line['Rhulk']))
            await rhulk.bot.get_channel(channel).send(line['Rhulk'])
        elif 'Calus' in line:
            async with calus.bot.get_channel(channel).typing():
                await asyncio.sleep(0.05 * len(line['Calus']))
            await calus.bot.get_channel(channel).send(line['Calus'])
        elif 'Drifter' in line:
            async with drifter.bot.get_channel(channel).typing():
                await asyncio.sleep(0.05 * len(line['Drifter']))
            await drifter.bot.get_channel(channel).send(line['Drifter'])
        elif 'Nezarec' in line:
            async with nezarec.bot.get_channel(channel).typing():
                await asyncio.sleep(0.05 * len(line['Nezarec']))
            await nezarec.bot.get_channel(channel).send(line['Nezarec'])
        
        await asyncio.sleep(round(random.uniform(1.0, 8.0), 1))
        
#* Creates the prompt for generating the random conversation
def create_prompt(first_speaker, topic, other_speakers):
    try:
        with open('data/character_info.json', "r") as f:
            character_info = json.load(f)
        
        if "all" in other_speakers:
            active_characters = list(character_info.keys())
            active_characters.remove(first_speaker)
        else:
            if len(other_speakers) == 0:
                rand_speak_amount = random.randint(1, len(character_info) - 1)
                while len(other_speakers) < rand_speak_amount:
                    char = random.choice(list(character_info))
                    if char not in other_speakers and char != first_speaker:
                        other_speakers.append(char)
            active_characters = {}
            for char in other_speakers:
                active_characters[char] = character_info[char]
                
        characters = "Characters: {}".format(character_info[first_speaker]["character"])
        personalities = character_info[first_speaker]["personality"]
        intros = character_info[first_speaker]["intro"]
        formatting = "Format as {}: TEXT".format(first_speaker)
        
        for char in active_characters:
            characters += "; {}".format(character_info[char]["character"])
            intros += "; {}".format(character_info[char]["intro"])
            personalities += ". {}".format(character_info[char]["personality"])
            formatting += ", {}: TEXT".format(char)

        prompt = ("Create dialogue set in Destiny universe. {}. {}. {}. "
        "Stay on topic. Be extremely entertaining, creative, and funny. {}. "
        "Characters speak in random order. Limit conversation to be 1000 characters. "
        "Topic: {}. {} starts.").format(characters, intros, personalities, formatting, topic, first_speaker)
        return prompt
    except Exception as e:
        return e

#*Resets topic list once all topics covered
def reset_topics():
    with open('data/topics.json', "r") as f:
        topics = json.load(f)
    new_topics = {}
    for k, v in topics.items():
        for t in v["topics"].keys():
            v["topics"][t]["chosen"] = False
        topics[k] = v
    with open('data/topics.json', 'w') as f:
        f.write(json.dumps(topics, indent=4))
    
    return new_topics

#* Generating the new random conversation
def generate_random_conversation(first_speaker="Rhulk", topic=None):
    log = open('log.txt', 'a')
    try:
        if topic is None:
            with open('data/topics.json', "r") as f:
                topics = json.load(f)
            
            available_topics = {}
            
            for category, info in topics.items():
                avail_topics = [k for k, v in info["topics"].items() if v["chosen"] is False]
                if len(avail_topics) != 0:
                    for k in avail_topics:
                        available_topics[category] = {"weight": info["weight"],
                                                      "topics": {k: info["topics"][k]}}
            
            if len(available_topics) == 0:
                available_topics = reset_topics()
            
            weights = {}
            
            for _, (k, v) in enumerate(available_topics.items()):
                weights[k] = v["weight"]
            
            
            chosen_key = random.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]
            chosen_topic = random.choice(list(available_topics[chosen_key]["topics"]))
            
            other_speakers = available_topics[chosen_key]["topics"][chosen_topic]["req_membs"]

            if first_speaker in other_speakers:
                other_speakers.remove(first_speaker)
            
            topics[chosen_key]["topics"][chosen_topic]["chosen"] = True
            with open('data/topics.json', 'w') as f:
                f.write(json.dumps(topics, indent=4))
        else:
            chosen_topic = topic
            other_speakers = ["all"]
            
        prompt = create_prompt(first_speaker, chosen_topic, other_speakers)
        
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=[{'role':'system', 'content': prompt}],
            n=1,
            temperature=1.1,
            frequency_penalty=0.2,
            presence_penalty=0.1,
            max_tokens=1250
        )
        
        convo = (completion.choices[0].message.content).splitlines()

        log.write(f'Generated a conversation with the topic: {chosen_topic}: \n{convo}\n\n')
        
        formatted_convo = []
        for line in convo:
            if "Rhulk: " in line:
                formatted_convo.append({'Rhulk': line.split(': ', 1)[1]})
            elif "Calus: " in line:
                formatted_convo.append({'Calus': line.split(': ', 1)[1]})
            elif "Drifter: " in line:
                formatted_convo.append({'Drifter': line.split(': ', 1)[1]})
            elif "Nezarec: " in line:
                formatted_convo.append({'Nezarec': line.split(': ', 1)[1]})
        
        log.close()
        return formatted_convo, chosen_topic
    except Exception as e:
        log.write('Encountered an error when generating a conversation: ' + e + '\n\n')
        log.close()
        return e


#? Random Conversation Commands


#* Manually generate a random or specific conversation with Rhulk being the first speaker
@rhulk.bot.tree.command(name="rhulk_start_conversation", description="Have Rhulk start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.")
async def rhulk_start_conversation(interaction: discord.Interaction, topic: str=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        convo, chosen_topic = generate_random_conversation('Rhulk', topic)
        await interaction.followup.send(f'*{interaction.user.display_name} wanted to hear our conversation about* ***{chosen_topic}.*** *Here is how it unfolded:*')
        
        await send_messages(convo, interaction.channel_id)
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
        await interaction.followup.send(f'*{interaction.user.display_name}, my most loyal Shadow, asked Rhulk and I to talk about:* ***{chosen_topic}!*** *Here is how that went:*')
        
        await send_messages(convo, interaction.channel_id)
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Calus: ' + e + '\n\n')
        await interaction.followup.send('Hmmm, I do not quite remember how the conversation went. (Bug Radiolorian for future fixes)')
    log.close()

#* Manually generate a random or specific conversation with Drifter being the first speaker
@drifter.bot.tree.command(name="drifter_start_conversation", description="Have Drifter start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.")
async def drifter_start_conversation(interaction: discord.Interaction, topic: str=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        convo, chosen_topic = generate_random_conversation('Drifter', topic)
        await interaction.followup.send(f'*My fellow crew member, Dredgen {interaction.user.display_name}, wanted to know about:* ***{chosen_topic}!*** *Well, here you go brother:*')
        
        await send_messages(convo, interaction.channel_id)
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Drifter: ' + e + '\n\n')
        await interaction.followup.send('Well well well, seems ol\' Drifter has done run out of ideas. (Bug Radiolorian for future fixes)')
    log.close()


#? Daily Conversation


#* Creating a new conversation at 1pm EST everyday
@tasks.loop(seconds = 45)
async def scheduledBotConversation():
    now = datetime.now(pytz.timezone('US/Eastern'))
    if now.hour == 13 and now.minute == 0:
        log = open('log.txt', 'a')
        try:
            with open('data/character_info.json', "r") as f:
                character_info = json.load(f)
            first_speaker = random.choice(list(character_info))
            
            
            for guild in rhulk.bot.guilds:
                if guild.name == "Victor's Little Pogchamps":
                    channel_id = get(guild.channels, name="rhulky-whulky").id
                    break
            
            convo, _ = generate_random_conversation(first_speaker)
            
            await send_messages(convo, channel_id)

            log.write('Finished random conversation topic as scheduled.\n\n')
        except Exception as e:
            log.write('Encountered an error in the Random Conversation Generation: ' + e + '\n\n')
        log.close()