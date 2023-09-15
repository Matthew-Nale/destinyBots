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


#? Conversation Generation


#* Creates the prompt for generating the random conversation
def create_prompt(first_speaker, topic, num_speakers=None):
    try:
        character_info = json.load(open('src/character_info.json'))
        
        active_characters = {}
        
        if num_speakers is None:
            num_additional_chars = random.randint(1, len(character_info) - 1)
        else:
            num_additional_chars = num_speakers - 1

        
        while len(active_characters) < num_additional_chars:
                k, v = random.choice(list(character_info.items()))
                if k not in active_characters and k != first_speaker:
                    active_characters[k] = v
                
        characters = "Characters: {}".format(character_info[first_speaker]["character"])
        personalities = character_info[first_speaker]["personality"]
        intros = character_info[first_speaker]["intro"]
        formatting = "Format as {}: TEXT".format(first_speaker)
        
        for char in active_characters:
            characters += "; {}".format(character_info[char]["character"])
            personalities += ". {}".format(character_info[char]["personality"])
            intros += "; {}".format(character_info[char]["intro"])
            formatting += ", {}: TEXT".format(char)
        
        prompt = ("Create dialogue set in Destiny universe. {}. {}. {}. "
        "Topic: {}. Stay on topic. Be extremely entertaining, creative, and funny. {}. "
        "Order of Speaking: completely random order. Limit conversation to be under 10 lines "
        "of dialogue. {} starts.").format(characters, intros, personalities, topic, formatting, first_speaker)
        
        return prompt
    except Exception as e:
        return e

#* Generating the new random conversation
def generate_random_conversation(first_speaker="Rhulk", topic=None, num_speakers=None):
    log = open('log.txt', 'a')
    try:
        if topic is None:
            topics = json.load(open('topics.json'))
            weights = {}
            for _, (k, v) in enumerate(topics.items()):
                weights[k] = v["weight"]
            chosen_key = random.choices(list(weights.keys()), weights=list(weights.values()))[0]
            chosen_topic = topics[chosen_key]["topics"][random.randint(0, len(topics[chosen_key]["topics"]) - 1)]
        else:
            chosen_topic = topic
        prompt = create_prompt(first_speaker, chosen_topic, num_speakers)
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=[{'role':'system', 'content': prompt}],
            n=1,
            temperature=1.1,
            frequency_penalty=0.1,
            max_tokens=1024
        )
        
        convo = (completion.choices[0].message.content).splitlines()
        while "" in convo:
            convo.remove("")
            
        log.write(f'Generated a conversation with the topic: {chosen_topic}: \n{convo}\n\n')
        
        formatted_convo = []
        for line in convo:
            if "Rhulk: " in line:
                formatted_convo.append({'Rhulk': line.split(': ', 1)[1]})
            elif "Calus: " in line:
                formatted_convo.append({'Calus': line.split(': ', 1)[1]})
            elif "Drifter: " in line:
                formatted_convo.append({'Drifter': line.split(': ', 1)[1]})
        
        log.close()
        return formatted_convo, chosen_topic
    except Exception as e:
        log.write('Encountered an error when generating a conversation: ' + e + '\n\n')
        log.close()
        return e


#? Random Conversation Commands


#* Manually generate a random or specific conversation with Rhulk being the first speaker
@rhulk.bot.tree.command(name="rhulk_start_conversation", description="Have Rhulk start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.", 
                       num_speakers="How many speakers should be present? Leave empty for a random amount.")
async def rhulk_start_conversation(interaction: discord.Interaction, topic: str=None, num_speakers: int=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        character_info = json.load(open('src/character_info.json'))
        num_speakers = max(2, min(num_speakers, len(character_info)))
        
        convo, chosen_topic = generate_random_conversation('Rhulk', topic, num_speakers)
        await interaction.followup.send(f'*{interaction.user.display_name} wanted to hear Calus and I\'s conversation about* ***{chosen_topic}.*** *Here is how it unfolded:*')
        for line in convo:
            if 'Rhulk' in line:
                async with rhulk.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Rhulk']))
                await rhulk.bot.get_channel(interaction.channel_id).send(line['Rhulk'])
            elif 'Calus' in line:
                async with calus.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Calus']))
                await calus.bot.get_channel(interaction.channel_id).send(line['Calus'])
            elif 'Drifter' in line:
                async with drifter.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Drifter']))
                await drifter.bot.get_channel(interaction.channel_id).send(line['Drifter'])
            await asyncio.sleep(round(random.uniform(2.0, 8.0), 1))
        
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Rhulk: ' + e + '\n\n')
        await interaction.followup.send('Hmmm, I do not quite remember how the conversation went. (Bug Radiolorian for future fixes)')
    log.close()

#* Manually generate a random or specific conversation with Calus being the first speaker
@calus.bot.tree.command(name="calus_start_conversation", description="Have Calus start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.",
                       num_speakers="How many speakers should be present? Leave empty for a random amount.")
async def calus_start_conversation(interaction: discord.Interaction, topic: str=None, num_speakers: int=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        character_info = json.load(open('src/character_info.json'))
        num_speakers = max(2, min(num_speakers, len(character_info)))
        
        convo, chosen_topic = generate_random_conversation('Calus', topic, num_speakers)
        await interaction.followup.send(f'*{interaction.user.display_name}, my most loyal Shadow, asked Rhulk and I to talk about: {chosen_topic}! Here is how that went:*')
        for line in convo:
            if 'Rhulk' in line:
                async with rhulk.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Rhulk']))
                await rhulk.bot.get_channel(interaction.channel_id).send(line['Rhulk'])
            elif 'Calus' in line:
                async with calus.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Calus']))
                await calus.bot.get_channel(interaction.channel_id).send(line['Calus'])
            elif 'Drifter' in line:
                async with drifter.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Drifter']))
                await drifter.bot.get_channel(interaction.channel_id).send(line['Drifter'])
            await asyncio.sleep(round(random.uniform(2.0, 8.0), 1))
        
    except Exception as e:
        log.write('Encountered an error in the Random Conversation Generation for Calus: ' + e + '\n\n')
        await interaction.followup.send('Hmmm, I do not quite remember how the conversation went. (Bug Radiolorian for future fixes)')
    log.close()

#* Manually generate a random or specific conversation with Drifter being the first speaker
@drifter.bot.tree.command(name="drifter_start_conversation", description="Have Drifter start a conversation with the other bots!")
@app_commands.describe(topic="What should the topic be about? Leave empty for a randomly picked one.",
                       num_speakers="How many speakers should be present? Leave empty for a random amount.")
async def drifter_start_conversation(interaction: discord.Interaction, topic: str=None, num_speakers: int=None):
    log = open('log.txt', 'a')
    try:
        await interaction.response.defer()
        
        character_info = json.load(open('src/character_info.json'))
        num_speakers = max(2, min(num_speakers, len(character_info)))
        
        convo, chosen_topic = generate_random_conversation('Drifter', topic, num_speakers)
        await interaction.followup.send(f'*My fellow Dredgen {interaction.user.display_name} wanted to know about:* ***{chosen_topic}!*** *Well, here you go brother:*')
        for line in convo:
            if 'Rhulk' in line:
                async with rhulk.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Rhulk']))
                await rhulk.bot.get_channel(interaction.channel_id).send(line['Rhulk'])
            elif 'Calus' in line:
                async with calus.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Calus']))
                await calus.bot.get_channel(interaction.channel_id).send(line['Calus'])
            elif 'Drifter' in line:
                async with drifter.bot.get_channel(interaction.channel_id).typing():
                    await asyncio.sleep(0.03 * len(line['Drifter']))
                await drifter.bot.get_channel(interaction.channel_id).send(line['Drifter'])
            await asyncio.sleep(round(random.uniform(2.0, 8.0), 1))
        
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
            character_info = json.load(open('src/character_info.json'))
            first_speaker = random.choice(list(character_info))
            num_speakers = random.randint(2, len(character_info))
            
            for guild in rhulk.bot.guilds:
                if guild.name == "Victor's Little Pogchamps":
                    channel_id = get(guild.channels, name="rhulky-whulky").id
                    break
            
            convo, _ = generate_random_conversation(first_speaker, num_speakers=num_speakers)
            
            for line in convo:
                if 'Rhulk' in line:
                    async with rhulk.bot.get_channel(channel_id).typing():
                        await asyncio.sleep(0.03 * len(line['Rhulk']))
                    await rhulk.bot.get_channel(channel_id).send(line['Rhulk'])
                elif 'Calus' in line:
                    async with calus.bot.get_channel(channel_id).typing():
                        await asyncio.sleep(0.03 * len(line['Calus']))
                    await calus.bot.get_channel(channel_id).send(line['Calus'])
                elif 'Drifter' in line:
                    async with drifter.bot.get_channel(channel_id).typing():
                        await asyncio.sleep(0.03 * len(line['Drifter']))
                    await drifter.bot.get_channel(channel_id).send(line['Drifter'])
                
                await asyncio.sleep(round(random.uniform(2.0, 8.0), 1))

            log.write('Finished random conversation topic as scheduled.\n\n')
        except Exception as e:
            log.write('Encountered an error in the Random Conversation Generation: ' + e + '\n\n')
        log.close()