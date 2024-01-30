import os
import json
import discord

from discord import app_commands
from dotenv import load_dotenv
from src.bot import Bot

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

@tower_pa.bot.event
async def on_guild_join(guild: discord.Guild) -> (None):
    """
    Sends entrance message to guild on join

    :param guild (discord.Guild): Server that bot has joined
    """
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Hello Guardians. Wonderful to see you in {}!".format(guild.name))
    log.write(f'Tower PA joined a new server: {guild.name}\n\n')
    log.close()

@tower_pa.bot.event
async def on_ready():
    await tower_pa.on_ready()

@tower_pa.bot.tree.command(name="topics", description="View the saved topics that the bots can chat over!")
async def topics(interaction: discord.Interaction):
    try:
        topics = json.load(open('data/text_conversations.json'))["topics"]
        await interaction.response.defer()
        await interaction.followup.send(f'Guardian, we\'ve intercepted a transmission between the other bots. They will probably talk about one of these:', ephemeral=True)
        for key, value in topics.items():
            response = f'**{key}:**\n'
            for k, v in value["topics"].items():
                if v['chosen']:
                    response += f'~~{k}~~\n'
                else:
                    response += f'{k}\n'
            await interaction.followup.send(f'{response}', ephemeral=True)
    except Exception as e:
        print(e)

@tower_pa.bot.tree.command(name="add_topic", description="Add a topic that can be used for the daily conversation!")
@app_commands.describe(topic="What topic should be added to the list?")
async def add_topic(interaction: discord.Interaction, topic: str=None):
    if topic != None:
        topics = json.load(open('data/text_conversations.json'))
        if topic not in topics["topics"]['misc']["topics"]:
            topics["topics"]['misc']["topics"][topic] = { "chosen": False,
                                                "req_membs": ["all"]}
            with open('data/text_conversations.json', 'w') as f:
                log = open('log.txt', 'a')
                f.write(json.dumps(topics, indent=4))
                log.write(f'Added a new topic to the list: {topic}\n\n')
                log.close()
                await interaction.response.send_message(f'Good choice, {interaction.user.global_name}. We\'ll inform the others to talk about **{topic}** in the future.')
        else:
            await interaction.response.send_message(f'The others will already talk about that topic, {interaction.user.global_name}. (Already in list)')
    else:
        await interaction.response.send_message(f'{interaction.user.global_name}? Come in {interaction.user.global_name}! (Must input something)')

@tower_pa.bot.tree.command(name="voice_opt_in", description="Manually opt in for voice chat interaction with the bots")
async def voice_opt_in(interaction: discord.Interaction):
    try:
        registered_users = json.load(open('data/voice_conversations.json'))
        if interaction.user.id in registered_users["registered_users"]:
            await interaction.response.send_message("Already registered!", ephemeral=True)
        else:
            registered_users["registered_users"].append(interaction.user.id)
            with open('data/voice_conversations.json', "w") as f:
                f.write(json.dumps(registered_users, indent=4))
            await interaction.response.send_message("Registered for voice conversations!", ephemeral=True)
    except:
        interaction.response.send_message('Encountered an unknown error with registering, please try again later.', ephemeral=True)
        
@tower_pa.bot.tree.command(name="updates", description="View the most recent update to the bots")
async def updates(interaction: discord.Interaction):
    with open("UPDATES.md", "r") as f:
        await interaction.response.send_message(content=f.read())