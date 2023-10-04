import os
import json
from discord import app_commands
from dotenv import load_dotenv
from src.elevenlab import *
from src.bot import *


#? Initializations and global values


load_dotenv()
TOWER_TOKEN = os.getenv('DISCORD_TOKEN_TOWER')

tower_pa = Bot(
    _name="Tower",
    _discord_token=TOWER_TOKEN,
    _use_voice=False,
    _use_text=False
)


#? Tower Bot Commands

#* Setup initial things on server join
@tower_pa.bot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Hello Guardians. Wonderful to see you in {}!".format(guild.name))
    log.write(f'Tower PA joined a new server: {guild.name}\n\n')
    log.close()

#* Calibration for starting of Nezarec bot
@tower_pa.bot.event
async def on_ready():
    await tower_pa.bot.load_extension('src.chime_in')
    await tower_pa.on_ready()

#* Shows the list of random topics to be used daily or with the /generate_conversation command
@tower_pa.bot.tree.command(name="topics", description="View the saved topics that the bots can chat over!")
async def topics(interaction: discord.Interaction):
    topics = json.load(open('data/topics.json'))
    response = ""
    for _, (key, value) in enumerate(topics.items()):
        response += f'**{key}:**\n'
        for k, v in value["topics"].items():
            if v['chosen']:
                response += f'~~{k}~~\n'
            else:
                response += f'{k}\n'
        response += '\n'
    await interaction.response.send_message(f'Guardian, we\'ve intercepted a transmission between the other bots. They will probably talk about one of these: \n\n{response}', ephemeral=True)

#* Add a topic to the topic list
@tower_pa.bot.tree.command(name="add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def add_topic(interaction: discord.Interaction, topic: str=None):
    if topic != None:
        topics = json.load(open('data/topics.json'))
        if topic not in topics['misc']["topics"]:
            topics['misc']["topics"][topic] = { "chosen": False,
                                                "req_membs": ["all"]}
            with open('data/topics.json', 'w') as f:
                log = open('log.txt', 'a')
                f.write(json.dumps(topics, indent=4))
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                await interaction.response.send_message(f'Good choice, {interaction.user.global_name}. We\'ll inform the others to talk about **{topic}** in the future.')
        else:
            await interaction.response.send_message(f'The others will already talk about that topic, {interaction.user.global_name}. (Already in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}? Come in {interaction.user.global_name}! (Must input something)')