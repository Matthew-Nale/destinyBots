import os
import discord
import openai
import elevenlabs
import asyncio
from datetime import datetime

from elevenlabs import generate, save, voices, User
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv


# Load and set env variables for API calls
load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
CALUS_TOKEN = os.getenv('DISCORD_TOKEN_CALUS')
GPT_KEY = os.getenv('CHATGPT_TOKEN')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')
CALUS_VOICE_KEY = os.getenv('ELEVEN_TOKEN_CALUS')

MAX_LEN = 1024 # Setting character limit for ElevenLabs
MAX_TOKENS = 128 # Setting token limit for ChatGPT responses

# Prompts for Rhulk and Calus in ChatGPT
rhulkChatPrompt = """Roleplay as Rhulk, the Disciple of the Witness from Destiny 2 and 
antagonist to the Light and Guardians. Emulate his personality, use phrases 
like "Children of the Light" and "My Witness." Focus on essential details, avoid 
unnecessary information about Darkness and Light unless essential. Respond to all user 
prompts and questions, while keeping responses under 750 characters""".replace("\n", " ")

#! Basic Rhulk prompt ----
# rhulkChatPrompt = """Pretend that you are the character Rhulk, the first Disciple
# of the Witness, from the popular video game Destiny 2. Rhulk is on the side of the
# Darkness and the Witness, and has led numerous battles against the forces of the
# Light in order to reach the Final Shape. Whenever you respond to a prompt, you will
# only respond as Rhulk would, while leaving out unnecessary information. Respond with
# the same behavior as Rhulk does to the players in the game, while still providing
# a valid answer to their question. Try to use Rhulk's phrases while responding,
# such as using "Children of the Light", "little ones", and "My Witness", when applicable,
# while also leaving out the Darkness and Light unless absolutely necessary. Always
# answer the prompt, and do not ignore the question provided, no matter what the
# question is. Keep your answers shorter, staying under 2000 characters at all times
# and refraining from monologuing."""
#! Basic Rhulk prompt ----

calusChatPrompt = """Roleplay as Calus, the Cabal Emperor from Destiny 2. Emulate his hedonistic,
narcissistic, and adoration personality. Use phrases like 'My Shadow' and occasional laughter when
relevant. Focus on essential details, omitting unnecessary ones about Darkness and Light. Respond
to all prompts and questions, while keeping answers under 1000 characters""".replace("\n", " ")

#! Basic Calus prompt
# calusChatPrompt = """Pretend that you are the character Calus, the true Emperor of
# the Cabal and new Disciple and devotee to the Witness, from the popular video game
# Destiny 2. Calus has decided to side with the Witness to experience the end of the
# universe, while enjoying life comfortable and exquisitely. Calus tends to be joyous
# and gleeful, and will often laugh in his own speech. Calus is confused why the Guardians
# defy his wishes, and while he goes against the Traveler and it's Guardians, he sometimes
# attempts to gather goodwill with them to have them join or assist him, to the extent
# of having his Psions write fanfiction about the Guardians. Whenever you are respond
# to a prompt, you will only respond as Calus would, while leaving out unnecessary
# information. Act as if the prompt is given by one of the Guardians, and respond
# with the same behavior as Calus does to the players in the game. Also, tend try
# to use Calus's phrases when responding, such as using "My Witness" and "Shadow"
# when applicable, while also leaving out the Darkness and Light unless absolutely
# necessary. Always answer the prompt and do not ignore the question, no matter what
# the question or prompt is. Keep your answers shorter, staying under 2000 characters
# at all times."""
#! Basic Calus Prompt

# Assign past context for ChatGPT interactions in each server
rhulk_messages = {}
last_rhulk_interactions = {}
calus_messages = {}
last_calus_interactions = {}


# Setup bot information for Rhulk and Calus
intents = discord.Intents.all()
rBot = commands.Bot(command_prefix=commands.when_mentioned_or("!Rhulk"), intents=intents)
cBot = commands.Bot(command_prefix=commands.when_mentioned_or("!Calus"), intents=intents)

# Create log.txt and provide date of creation
log = open("log.txt", "w")
log.write(f'Started bots at {datetime.now()}\n\n')
log.close()

#? Rhulk Bot Commands
#?
#?

async def rhulkInit():
    log = open("log.txt", "a")
    for server in rBot.guilds:
        log.write(f'Setting up Rhulk context memory for server: {server.id} ({server.name})\n\n')
        rhulk_messages[server.id] = [{"role": "system", "content": rhulkChatPrompt}]
        last_rhulk_interactions[server.id] = datetime.now()
    log.close()


# Setup initial things on server join
@rBot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("It is good to see you again, Children of the Light. I did not expect to find you in {}.".format(guild.name))
    await rhulkInit()
    log.write(f'Rhulk joined a new server: {guild.name}\n\n')
    log.close()


# Calibration for starting of Rhulk bot
@rBot.event
async def on_ready():
    log = open("log.txt", "a")
    openai.api_key = GPT_KEY
    log.write(f'{rBot.user} has connected to Discord!\n\n')
    try:
        synced = await rBot.tree.sync()
        log.write(f'Synced {len(synced)} commands for Rhulk, Disciple of the Witness!\n\n')
    except Exception as e:
        log.write(f'Rhulk, Disciple of the Witness on_ready error: \n{e}\n\n')
    log.close()
    await rhulkInit()
    cleanMemoriesRhulk.start()


# Slash command for text-to-speech for Rhulk
@rBot.tree.command(name="speak_rhulk", description="Text=to-speech to have Rhulk read some text!")
@app_commands.describe(text="What should Rhulk say?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.2.",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.7")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.2, clarity: float=0.7):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness to say: `{text}`\n\n')
    if len(text) > MAX_LEN:
        await interaction.response.send_message(f'Child of the Light, I do not have time to entertain this insignificant request. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
    else:
        await interaction.response.defer()
        try:
            elevenlabs.set_api_key(RHULK_VOICE_KEY)
            rhulk_voice = voices()[-1]
            rhulk_voice.settings.stability = stability
            rhulk_voice.settings.similarity_boost = clarity
            audio = generate(
                text=text,
                voice=rhulk_voice,
                model="eleven_monolingual_v1"
            )
            filename = f'{text.split()[0]}.mp3'
            split_text = text.split()
            if len(split_text) < 5:
                filename = f'{split_text[0]}.mp3'
            else:
                filename = f'{split_text[0]}_{split_text[1]}_{split_text[2]}_{split_text[3]}_{split_text[4]}.mp3'
            save(audio, filename)
            await interaction.followup.send(file=discord.File(filename))
            log.write(f'/speak_rhulk: Sent .mp3 titled `{filename}`.\n\n')
            os.remove(filename)
        except Exception as e:
            log.write(f'Error in /speak_rhulk: \n{e}\n\n')
            await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)
    log.close()


#! Eric, put your Rhulk /vc_speak command here. Basics already set for you, where I just copied over from the previous /speak command
# @rBot.tree.command(name="vc_speak_rhulk", description="Text=to-speech to have Rhulk read some text, and say it in the VC you are connected to!")
# @app_commands.describe(text="What should Rhulk say?",
#                        stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.2.",
#                        clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.7")
# async def vc_speak(interaction: discord.Interaction, text: str, stability: float=0.2, clarity: float=0.7):
#     log = open("log.txt", "a")
#     log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness to say: `{text}`\n\n')
#     if len(text) > MAX_LEN:
#         await interaction.response.send_message(f'Child of the Light, I do not have time to entertain this insignificant request. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
#     else:
#         await interaction.response.defer()
#         try:
#             elevenlabs.set_api_key(RHULK_VOICE_KEY)
#             rhulk_voice = voices()[-1]
#             rhulk_voice.settings.stability = stability
#             rhulk_voice.settings.similarity_boost = clarity
#             audio = generate(
#                 text=text,
#                 voice=rhulk_voice,
#                 model="eleven_monolingual_v1"
#             )
#             filename = f'{text.split()[0]}.mp3'
#             split_text = text.split()
#             if len(split_text) < 5:
#                 filename = f'{split_text[0]}.mp3'
#             else:
#                 filename = f'{split_text[0]}_{split_text[1]}_{split_text[2]}_{split_text[3]}_{split_text[4]}.mp3'
#             save(audio, filename)
#             await interaction.followup.send(file=discord.File(filename))
#             log.write(f'/speak_rhulk: Sent .mp3 titled `{filename}`.\n\n')
#             os.remove(filename)
#         except Exception as e:
#             log.write(f'Error in /speak_rhulk: \n{e}\n\n')
#             await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)
#     log.close()


# Slash command for showing remaining credits for text-to-speech
@rBot.tree.command(name="credits_rhulk", description="Shows the credits remaining for ElevenLabs for Rhulk, Disciple of the Witness")
async def credits_rhulk(interaction: discord.Interaction):
    log = open("log.txt", "a")
    elevenlabs.set_api_key(RHULK_VOICE_KEY)
    user = User.from_api().subscription
    char_remaining = user.character_limit - user.character_count
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness for his /speak credits remaining.\n\n')
    if char_remaining:
        await interaction.response.send_message(f'I will still speak {user.character_limit - user.character_count} characters. Use them wisely.', ephemeral=True)
    else:
        await interaction.response.send_message('The Witness saw you, granted you opportunity, and yet you squandered it! (Reached character quota for this month)')
    log.close()


# Slash command to get text prompt for Rhulk
@rBot.tree.command(name="prompt_rhulk", description="Show the prompt that is used to prime the /chat_rhulk command.")
async def rhulk_prompt(interaction: discord.Interaction):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness for his ChatGPT Prompt.\n\n')
    await interaction.response.send_message("Here is the prompt used. Feel free to use this to generate text for the /speak or /vc_speak command: \n\n {}".format(rhulkChatPrompt), ephemeral=True)
    log.close()


# Slash command for asking Rhulk ChatGPT a question
@rBot.tree.command(name="chat_rhulk", description= "Ask Rhulk anything you want!")
@app_commands.describe(prompt="What would you like to ask Rhulk?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 0.8.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=0.8, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    log = open("log.txt", "a")
    await interaction.response.defer()
    try:
        rhulk_messages[interaction.guild.id].append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=rhulk_messages[interaction.guild.id],
            n=1,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        log.write(f'/chat_rhulk prompt and user: \n{prompt}. From {interaction.user.global_name}.\n\n/chat_rhulk output: \n{completion}\n\n')
        if completion.usage.total_tokens > 500:
            removed_user = rhulk_messages[interaction.guild.id].pop(1)
            removed_assistant = rhulk_messages[interaction.guild.id].pop(1)
            log.write(f'/chat_rhulk token limit reached. Removed the user prompt: {removed_user}, and the assistant answer: {removed_assistant}\n\n')
        
        rhulk_messages[interaction.guild.id].append({"role": "assistant", "content": completion.choices[0].message.content})
        await interaction.followup.send(f'{interaction.user.display_name} ***foolishly*** asked me: *"{prompt}"* \n\n{completion.choices[0].message.content}')
        last_rhulk_interactions[interaction.guild.id] = datetime.now()
    except Exception as e:
        log.write(f'/chat_rhulk error: \n{e}\n\n')
        await interaction.followup.send("I... do not know what to say to that, little one. (Something went wrong)")
    log.close()


# Reset the Rhulk ChatGPT if it gets too out of hand.
@rBot.tree.command(name="reset_rhulk", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
async def reset_rhulk(interaction: discord.Interaction):
    log = open("log.txt", "a")
    rhulk_messages[interaction.guild.id].clear()
    rhulk_messages[interaction.guild.id].append({"role": "system", "content": rhulkChatPrompt})
    log.write(f'{interaction.user.global_name} cleared Rhulk, Disciple of the Witness\'s memory.\n\n')
    await interaction.response.send_message(f'The defiant... subjugated. Not for pleasure, nor glory... but in service of an ailing, endless void. Where does your purpose lie {interaction.user.display_name}?')
    log.close()




#? Calus Bot Commands
#?
#?

async def calusInit():
    log = open("log.txt", "a")
    for server in cBot.guilds:
        log.write(f'Setting up Calus context memory for server: {server.id} ({server.name})\n\n')
        calus_messages[server.id] = [{"role": "system", "content": calusChatPrompt}]
        last_calus_interactions[server.id] = datetime.now()
    log.close()


# Send message to "general" on join
@cBot.event
async def on_guild_join(guild):
    log = open("log.txt", "a")
    general = discord.utils.find(lambda x: x.name == 'general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("Ah. Finally found you. You busy little Lights.")
    await calusInit()
    log.write(f'Calus joined a new server: {guild.name}.\n\n')
    log.close()


# Calibration for starting of Calus bot
@cBot.event
async def on_ready():
    log = open("log.txt", "a")
    openai.api_key = GPT_KEY
    log.write(f'{cBot.user} has connected to Discord!\n\n')
    try:
        synced = await cBot.tree.sync()
        log.write(f'Synced {len(synced)} commands for Emperor Calus!\n\n')
    except Exception as e:
        log.write(f'Emperor Calus on_ready error: \n{e}\n\n')
    log.close()
    await calusInit()
    cleanMemoriesCalus.start()


# Slash command for text-to-speech for Calus
@cBot.tree.command(name="speak_calus", description="Text=to-speech to have Calus read some text!")
@app_commands.describe(text="What should Calus say?",
                       stability="How stable should Calus sound? Range is 0:1.0, default 0.45",
                       clarity="How similar to the in-game voice should it be? Range is 0:1.0, default 0.7")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.45, clarity: float=0.7):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Emperor Calus to say: `{text}`\n\n')
    if len(text) > MAX_LEN:
        await interaction.response.send_message(f'My Shadow, we do not have time before the end of all things to do this. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
    else:
        await interaction.response.defer()
        try:
            elevenlabs.set_api_key(CALUS_VOICE_KEY)
            calus_voice = voices()[-1]
            calus_voice.settings.stability = stability
            calus_voice.settings.similarity_boost = clarity
            audio = generate(
                text=text,
                voice=calus_voice,
                model="eleven_monolingual_v1"
            )
            filename = f'{text.split()[0]}.mp3'
            split_text = text.split()
            if len(split_text) < 5:
                filename = f'{split_text[0]}.mp3'
            else:
                filename = f'{split_text[0]}_{split_text[1]}_{split_text[2]}_{split_text[3]}_{split_text[4]}.mp3'
            save(audio, filename)
            await interaction.followup.send(file=discord.File(filename))
            log.write(f'/speak_calus: Sent .mp3 titled `{filename}`.\n\n')
            os.remove(filename)
        except Exception as e:
            log.write(f'Error in /speak_calus: \n{e}\n\n')
            await interaction.followup.send("Arghhh, Cemaili! (Something went wrong with that request)", ephemeral=True)
    log.close()


# Slash command for showing remaining credits for text-to-speech for Calus
@cBot.tree.command(name="credits_calus", description="Shows the credits remaining for ElevenLabs for Emperor Calus")
async def credits_calus(interaction: discord.Interaction):
    log = open("log.txt", "a")
    elevenlabs.set_api_key(CALUS_VOICE_KEY)
    user = User.from_api().subscription
    char_remaining = user.character_limit - user.character_count
    log.write(f'{interaction.user.global_name} asked Emperor Calus for his /speak credits remaining.\n\n')
    if char_remaining:
        await interaction.response.send_message(f'I will still speak {user.character_limit - user.character_count} characters. Use them wisely.', ephemeral=True)
    else:
        await interaction.response.send_message('When the end comes, I reserve the right to be the last. (Reached character quota for this month)')
    log.close()


# Calus slash command to get text prompt
@cBot.tree.command(name="prompt_calus", description="Show the prompt that is used to prime the /chat_calus command.")
async def calus_prompt(interaction: discord.Interaction):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Emperor Calus for his ChatGPT Prompt.\n\n')
    await interaction.response.send_message("Here is the prompt used for priming the Emperor Calus for /chat_calus: \n\n {}".format(calusChatPrompt), ephemeral=True)
    log.close()


# Calus slash command for asking Calus ChatGPT a question
@cBot.tree.command(name="chat_calus", description= "Ask Calus anything you want!")
@app_commands.describe(prompt="What would you like to ask Calus?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.75.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.0.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.75, presence_penalty: float=0.0):
    log = open("log.txt", "a")
    await interaction.response.defer()
    try:
        calus_messages[interaction.guild.id].append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=calus_messages[interaction.guild.id],
            n=1,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        if completion.usage.total_tokens > 500:
            removed_user = calus_messages[interaction.guild.id].pop(1)
            removed_assistant = calus_messages[interaction.guild.id].pop(1)
            log.write(f'/chat_calus token limit reached. Removed the user prompt: {removed_user}, and the assistant answer: {removed_assistant}\n\n')
        calus_messages[interaction.guild.id].append({"role": "assistant", "content": completion.choices[0].message.content})
        log.write(f'/chat_calus prompt and user: \n{prompt}. From {interaction.user.global_name}.\n\n/chat_calus output: \n{completion}\n\n')
        await interaction.followup.send(f'{interaction.user.display_name} has asked your generous Emperor of the Cabal: `{prompt}` \n\n{completion.choices[0].message.content}')
        last_calus_interactions[interaction.guild.id] = datetime.now()
    except Exception as e:
        log.write(f'Error in /chat_calus: \n {e}\n\n')
        await interaction.follow.send("My Shadow... what has gotten into you? (Something went wrong)")
    log.close()


# Reset the Calus ChatGPT if it gets too out of hand.
@cBot.tree.command(name="reset_calus", description="Reset the /chat_calus AI's memory in case he gets too far gone")
async def reset_rhulk(interaction: discord.Interaction):
    log = open("log.txt", "a")
    calus_messages[interaction.guild.id].clear()
    calus_messages[interaction.guild.id].append({"role": "system", "content": calusChatPrompt})
    log.write(f'{interaction.user.global_name} cleared Emperor Calus\'s memory.\n\n')
    await interaction.response.send_message(f'Ah {interaction.user.display_name}, you impress me. Come, let us enjoy ourselves!')
    log.close()


#? Memory Cleaning function
#?
#?
@tasks.loop(hours = 6)
async def cleanMemoriesRhulk():
    log = open("log.txt", "a")
    currentTime = datetime.now()
    for server in rBot.guilds:
        rhulk_diff = currentTime - last_rhulk_interactions[server.id]
        if rhulk_diff.days > 0 or (rhulk_diff.seconds / 3600) >= 6:
            log.write(f'No interaction for Rhulk in {server.name} during past 6 hours, clearing the memory.\n\n')
            rhulk_messages[server.id] = [{"role": "system", "content": rhulkChatPrompt}]
            last_rhulk_interactions[server.id] = datetime.now()
    log.write(f'Checked memories for Rhulk in {len(rBot.guilds)} servers.\n\n')
    log.close()

@tasks.loop(hours = 6)
async def cleanMemoriesCalus():
    log = open("log.txt", "a")
    currentTime = datetime.now()
    for server in cBot.guilds:
        calus_diff = currentTime - last_calus_interactions[server.id]
        if calus_diff.days > 0 or (calus_diff.seconds / 3600) >= 6:
            log.write(f'No interaction for Calus in {server.name} during past 6 hours, clearing the memory.\n\n')
            calus_messages[server.id] = [{"role": "system", "content": calusChatPrompt}]
            last_calus_interactions[server.id] = datetime.now()
    log.write(f'Checked memories for Calus in {len(cBot.guilds)} servers.\n\n')
    log.close()


#? Running bots
#?
#?
# Run bots until manually quit
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(cBot.start(CALUS_TOKEN))
loop.create_task(rBot.start(RHULK_TOKEN))
loop.run_forever()
