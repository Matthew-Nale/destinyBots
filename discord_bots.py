import os
import discord
import openai
import elevenlabs
import asyncio
import random
import pytz
from datetime import datetime
from elevenlabs import generate, save, voices, User
from discord import app_commands
from discord.utils import get
from discord.ext import commands, tasks
from dotenv import load_dotenv


#? Initializations and global values


#* Load and set env variables for API calls
load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
CALUS_TOKEN = os.getenv('DISCORD_TOKEN_CALUS')
GPT_KEY = os.getenv('CHATGPT_TOKEN')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')
CALUS_VOICE_KEY = os.getenv('ELEVEN_TOKEN_CALUS')


MAX_LEN = 1024 # Setting character limit for ElevenLabs
MAX_TOKENS = 128 # Setting token limit for ChatGPT responses
CHAT_MODEL = "gpt-3.5-turbo"


#? Bot Class


class Bot:
    def __init__(self, _name, _discord_token, _voice_key, _chat_prompt):
        self.name = _name
        self.bot = commands.Bot(command_prefix=commands.when_mentioned_or('!{self.name}'), intents=discord.Intents.all())
        self.discord_token = _discord_token
        self.voice_key = _voice_key
        self.chat_prompt = _chat_prompt
        self.memory = {}
        self.last_interaction = {}
        
    async def botInit(self):
        log = open("log.txt", "a")
        for server in self.bot.guilds:
            log.write(f'Setting up {self.name} context memory for server: {server.id} ({server.name})\n\n')
            self.memory[server.id] = [{"role": "system", "content": self.chat_prompt}]
            self.last_interaction[server.id] = datetime.now()
        log.close()
    
    @tasks.loop(hours = 6)
    async def cleanMemories(self):
        log = open("log.txt", "a")
        currentTime = datetime.now()
        for server in self.bot.guilds:
            time_diff = currentTime - self.last_interaction[server.id]
            if time_diff.days > 0 or (time_diff.seconds / 3600) >= 6:
                log.write(f'No interaction for {self.name} in {server.name} during past 6 hours, clearing the memory.\n\n')
                self.memory[server.id] = [{"role": "system", "content": self.chat_prompt}]
                self.last_interaction[server.id] = datetime.now()
        log.close()


#* Setup Bot classes
rhulk = Bot('Rhulk', RHULK_TOKEN, RHULK_VOICE_KEY, 
            """Roleplay as Rhulk, the Disciple of the Witness from Destiny 2 and 
            antagonist to the Light and Guardians. Emulate his personality, use phrases 
            like "Children of the Light" and "My Witness." Focus on essential details, avoid 
            unnecessary information about Darkness and Light unless essential. Respond to all user 
            prompts and questions, while keeping responses under 1000 characters""".replace("\n", " "))


calus = Bot('Calus', CALUS_TOKEN, CALUS_VOICE_KEY, 
            """Roleplay as Calus, the Cabal Emperor from Destiny 2. Emulate his hedonistic,
            narcissistic, and adoration personality. Use phrases like 'My Shadow' and occasional laughter when
            relevant. Focus on essential details, omitting unnecessary ones about Darkness and Light. Respond
            to all prompts and questions, while keeping answers under 1000 characters""".replace("\n", " "))


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
    log = open("log.txt", "a")
    openai.api_key = GPT_KEY
    log.write(f'{rhulk.bot.user} has connected to Discord!\n\n')
    try:
        synced = await rhulk.bot.tree.sync()
        log.write(f'Synced {len(synced)} commands for Rhulk, Disciple of the Witness!\n\n')
    except Exception as e:
        log.write(f'Rhulk, Disciple of the Witness on_ready error: \n{e}\n\n')
    log.close()
    await rhulk.botInit()
    rhulk.cleanMemories.start()
    scheduledBotConversation.start()


#* Slash command for text-to-speech for Rhulk
@rhulk.bot.tree.command(name="rhulk_speak", description="Text-to-speech to have Rhulk speak some text!")
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
            elevenlabs.set_api_key(rhulk.voice_key)
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


#* Slash command for Rhulk VC text-to-speech
@rhulk.bot.tree.command(name="rhulk_vc_speak", description="Text-to-speech to have Rhulk speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Rhulk say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.2.",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.7")
async def rhulk_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.2, clarity: float=0.7):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness to say in the VC: `{text}`\n\n')
    await interaction.response.defer()
    if len(text) > MAX_LEN:
        await interaction.followup.send(f'Child of the Light, I do not have time to entertain this insignificant request. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
    else:
        channel = None
        if interaction.user.voice is None:
            if vc == "":
                log.write(f'{interaction.user.global_name} was not in the VC, could not send message.\n\n')
                await interaction.followup.send(f'{interaction.user.display_name}, do not waste my time if you are not here. (Must be in a VC or specify a valid VC)', ephemeral=True)
            else:
                for c in interaction.guild.voice_channels:
                    if c.name == vc:
                        log.write("Found a valid voice channel to speak in.\n\n")
                        channel = rhulk.bot.get_channel(c.id)
        else:
            channel = interaction.user.voice.channel
            
        if channel != None:
            try:
                elevenlabs.set_api_key(rhulk.voice_key)
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
                vc = await channel.connect()
                await asyncio.sleep(1)
                vc.play(discord.FFmpegPCMAudio(source=filename))
                while vc.is_playing():
                    await asyncio.sleep(2.5)
                vc.stop()
                await vc.disconnect()
                await interaction.followup.send(file=discord.File(filename))
                log.write(f'/vc_speak_rhulk: Sent .mp3 titled `{filename}`.\n\n')
                os.remove(filename)
            except Exception as e:
                log.write(f'Error in /vc_speak_rhulk: \n{e}\n\n')
                await vc.disconnect()
                await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)
        else:
            await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)
    log.close()


#* Slash command for showing remaining credits for text-to-speech
@rhulk.bot.tree.command(name="rhulk_credits", description="Shows the credits remaining for ElevenLabs for Rhulk, Disciple of the Witness")
async def rhulk_credits(interaction: discord.Interaction):
    log = open("log.txt", "a")
    elevenlabs.set_api_key(rhulk.voice_key)
    user = User.from_api().subscription
    char_remaining = user.character_limit - user.character_count
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness for his /rhulk_speak credits remaining.\n\n')
    if char_remaining:
        await interaction.response.send_message(f'I will still speak {user.character_limit - user.character_count} characters. Use them wisely.', ephemeral=True)
    else:
        await interaction.response.send_message('The Witness saw you, granted you opportunity, and yet you squandered it! (Reached character quota for this month)')
    log.close()


#* Slash command to get text prompt for Rhulk
@rhulk.bot.tree.command(name="rhulk_prompt", description="Show the prompt that is used to prime the /rhulk_chat command.")
async def rhulk_prompt(interaction: discord.Interaction):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Rhulk, Disciple of the Witness for his ChatGPT Prompt.\n\n')
    await interaction.response.send_message("Here is the prompt used. Feel free to use this to generate text for the /speak or /vc_speak command: \n\n {}".format(rhulk.chat_prompt), ephemeral=True)
    log.close()


#* Slash command for asking Rhulk ChatGPT a question
@rhulk.bot.tree.command(name="rhulk_chat", description= "Ask Rhulk anything you want!")
@app_commands.describe(prompt="What would you like to ask Rhulk?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 0.8.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.9.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.75.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=0.8, frequency_penalty: float=0.9, presence_penalty: float=0.75):
    log = open("log.txt", "a")
    await interaction.response.defer()
    try:
        rhulk.memory[interaction.guild.id].append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=rhulk.memory[interaction.guild.id],
            n=1,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        log.write(f'/chat_rhulk prompt and user: \n{prompt}. From {interaction.user.global_name}.\n\n/chat_rhulk output: \n{completion}\n\n')
        if completion.usage.total_tokens > 500:
            removed_user = rhulk.memory[interaction.guild.id].pop(1)
            removed_assistant = rhulk.memory[interaction.guild.id].pop(1)
            log.write(f'/chat_rhulk token limit reached. Removed the user prompt: {removed_user}, and the assistant answer: {removed_assistant}\n\n')
        
        rhulk.memory[interaction.guild.id].append({"role": "assistant", "content": completion.choices[0].message.content})
        await interaction.followup.send(f'{interaction.user.display_name} ***foolishly*** asked me: *"{prompt}"* \n\n{completion.choices[0].message.content}')
        rhulk.last_interaction[interaction.guild.id] = datetime.now()
    except Exception as e:
        log.write(f'/chat_rhulk error: \n{e}\n\n')
        await interaction.followup.send("I... do not know what to say to that, little one. (Something went wrong)")
    log.close()


#* Reset the Rhulk ChatGPT if it gets too out of hand.
@rhulk.bot.tree.command(name="rhulk_reset", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
async def rhulk_reset(interaction: discord.Interaction):
    log = open("log.txt", "a")
    rhulk.memory[interaction.guild.id].clear()
    rhulk.memory[interaction.guild.id].append({"role": "system", "content": rhulk.chat_prompt})
    log.write(f'{interaction.user.global_name} cleared Rhulk, Disciple of the Witness\'s memory.\n\n')
    await interaction.response.send_message(f'The defiant... subjugated. Not for pleasure, nor glory... but in service of an ailing, endless void. Where does your purpose lie {interaction.user.display_name}?')
    log.close()


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
    log = open("log.txt", "a")
    openai.api_key = GPT_KEY
    log.write(f'{calus.bot.user} has connected to Discord!\n\n')
    try:
        synced = await calus.bot.tree.sync()
        log.write(f'Synced {len(synced)} commands for Emperor Calus!\n\n')
    except Exception as e:
        log.write(f'Emperor Calus on_ready error: \n{e}\n\n')
    log.close()
    await calus.botInit()
    calus.cleanMemories.start()


#* Slash command for text-to-speech for Calus
@calus.bot.tree.command(name="calus_speak", description="Text-to-speech to have Calus speak some text!")
@app_commands.describe(text="What should Calus say?",
                       stability="How stable should Calus sound? Range is 0:1.0, default 0.3",
                       clarity="How similar to the in-game voice should it be? Range is 0:1.0, default 0.8")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.3, clarity: float=0.8):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Emperor Calus to say: `{text}`\n\n')
    if len(text) > MAX_LEN:
        await interaction.response.send_message(f'My Shadow, we do not have time before the end of all things to do this. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
    else:
        await interaction.response.defer()
        try:
            elevenlabs.set_api_key(calus.voice_key)
            calus_voice = voices()[-1]
            calus_voice.settings.stability = stability
            calus_voice.settings.similarity_boost = clarity
            text = text.replace(" ", '\n')
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
    

#* Slash command for Calus VC text-to-speech
@calus.bot.tree.command(name="calus_vc_speak", description="Text-to-speech to have Calus speak some text, and say it in the VC you are connected to!")
@app_commands.describe(text="What should Calus say in the VC?",
                       vc="(Optional) What VC to join?",
                       stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.4.",
                       clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.85")
async def calus_vc_speak(interaction: discord.Interaction, text: str, vc: str="", stability: float=0.3, clarity: float=0.8):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Emperor Calus to say in the VC: `{text}`\n\n')
    await interaction.response.defer()
    if len(text) > MAX_LEN:
        await interaction.response.send_message(f'My Shadow, we do not have time before the end of all things to do this. Please limit your text to below {MAX_LEN} characters. You are currently at {len(text)} characters.', ephemeral=True)
    else:
        channel = None
        if interaction.user.voice is None:
            if vc == "":
                log.write(f'{interaction.user.global_name} was not in the VC, could not send message.\n\n')
                await interaction.response.send_message(f'{interaction.user.display_name}, let us relax in the Pleasure Gardens instead. (Must be in a VC)', ephemeral=True)
            else:
                for c in interaction.guild.voice_channels:
                    if c.name == vc:
                        log.write("Found a valid voice channel to speak in.\n\n")
                        channel = calus.bot.get_channel(c.id)
        else:
            channel = interaction.user.voice.channel
        
        if channel != None:
            try:
                elevenlabs.set_api_key(CALUS_VOICE_KEY)
                calus_voice = voices()[-1]
                calus_voice.settings.stability = stability
                calus_voice.settings.similarity_boost = clarity
                text = text.replace(" ", '\n')
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
                vc = await channel.connect()
                await asyncio.sleep(1)
                vc.play(discord.FFmpegPCMAudio(source=filename))
                while vc.is_playing():
                    await asyncio.sleep(2.5)
                vc.stop()
                await vc.disconnect()
                await interaction.followup.send(file=discord.File(filename))
                log.write(f'/vc_speak_calus: Sent .mp3 titled `{filename}`.\n\n')
                os.remove(filename)
            except Exception as e:
                log.write(f'Error in /vc_speak_rhulk: \n{e}\n\n')
                await vc.disconnect()
                await interaction.followup.send("Arghhh, Cemaili! (Something went wrong with that request)", ephemeral=True)
        else:
            await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)
    log.close()


#* Slash command for showing remaining credits for text-to-speech for Calus
@calus.bot.tree.command(name="calus_credits", description="Shows the credits remaining for ElevenLabs for Emperor Calus")
async def calus_credits(interaction: discord.Interaction):
    log = open("log.txt", "a")
    elevenlabs.set_api_key(calus.voice_key)
    user = User.from_api().subscription
    char_remaining = user.character_limit - user.character_count
    log.write(f'{interaction.user.global_name} asked Emperor Calus for his /speak credits remaining.\n\n')
    if char_remaining:
        await interaction.response.send_message(f'I will still speak {user.character_limit - user.character_count} characters. Use them wisely.', ephemeral=True)
    else:
        await interaction.response.send_message('When the end comes, I reserve the right to be the last. (Reached character quota for this month)')
    log.close()


#* Calus slash command to get text prompt
@calus.bot.tree.command(name="calus_prompt", description="Show the prompt that is used to prime the /calus_chat command.")
async def calus_prompt(interaction: discord.Interaction):
    log = open("log.txt", "a")
    log.write(f'{interaction.user.global_name} asked Emperor Calus for his ChatGPT Prompt.\n\n')
    await interaction.response.send_message("Here is the prompt used for priming the Emperor Calus for /chat_calus: \n\n {}".format(calus.chat_prompt), ephemeral=True)
    log.close()


#* Calus slash command for asking Calus ChatGPT a question
@calus.bot.tree.command(name="calus_chat", description= "Ask Calus anything you want!")
@app_commands.describe(prompt="What would you like to ask Calus?",
                       temperature="How random should the response be? Range between 0.0:2.0, default is 1.2.",
                       frequency_penalty="How likely to repeat the same line? Range between -2.0:2.0, default is 0.75.",
                       presence_penalty="How likely to introduce new topics? Range between -2.0:2.0, default is 0.0.")
async def chat(interaction: discord.Interaction, prompt: str, temperature: float=1.2, frequency_penalty: float=0.75, presence_penalty: float=0.0):
    log = open("log.txt", "a")
    await interaction.response.defer()
    try:
        calus.memory[interaction.guild.id].append({"role": "user", "content": prompt})
        completion = openai.ChatCompletion.create(
            model=CHAT_MODEL,
            messages=calus.memory[interaction.guild.id],
            n=1,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )
        if completion.usage.total_tokens > 500:
            removed_user = calus.memory[interaction.guild.id].pop(1)
            removed_assistant = calus.memory[interaction.guild.id].pop(1)
            log.write(f'/chat_calus token limit reached. Removed the user prompt: {removed_user}, and the assistant answer: {removed_assistant}\n\n')
        calus.memory[interaction.guild.id].append({"role": "assistant", "content": completion.choices[0].message.content})
        log.write(f'/chat_calus prompt and user: \n{prompt}. From {interaction.user.global_name}.\n\n/chat_calus output: \n{completion}\n\n')
        await interaction.followup.send(f'{interaction.user.display_name} has asked your generous Emperor of the Cabal: `{prompt}` \n\n{completion.choices[0].message.content}')
        calus.last_interaction[interaction.guild.id] = datetime.now()
    except Exception as e:
        log.write(f'Error in /chat_calus: \n {e}\n\n')
        await interaction.follow.send("My Shadow... what has gotten into you? (Something went wrong)")
    log.close()


#* Reset the Calus ChatGPT if it gets too out of hand.
@calus.bot.tree.command(name="calus_reset", description="Reset the /calus_chat AI's memory in case he gets too far gone")
async def calus_reset(interaction: discord.Interaction):
    log = open("log.txt", "a")
    calus.memory[interaction.guild.id].clear()
    calus.memory[interaction.guild.id].append({"role": "system", "content": calus.chat_prompt})
    log.write(f'{interaction.user.global_name} cleared Emperor Calus\'s memory.\n\n')
    await interaction.response.send_message(f'Ah {interaction.user.display_name}, you impress me. Come, let us enjoy ourselves!')
    log.close()


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
@tasks.loop(minutes=1)
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


#* Create log.txt and provide date of creation
log = open("log.txt", "w")
log.write(f'Started bots at {datetime.now()}\n\n')
log.close()


#* Run bots until manually quit
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.create_task(calus.bot.start(calus.discord_token))
loop.create_task(rhulk.bot.start(rhulk.discord_token))
loop.run_forever()
