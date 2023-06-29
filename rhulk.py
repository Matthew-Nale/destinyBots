import os
import discord
import openai
import elevenlabs

from elevenlabs import generate, save, voices, User
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


# Load and set env variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
GPT_KEY = os.getenv('CHATGPT_TOKEN')
GPT_ORGANIZATION = os.getenv('CHATGPT_ORGANIZATION')
VOICE_KEY = os.getenv('ELEVEN_TOKEN')

MAX_LEN = 256

chatPrompt = """In the popular video game Destiny 2, one of the raid bosses is known as Rhulk, 
the first disciple of the witness. Rhulk has been trapped for ages in his pyramid ship inside of the traitor 
Savathuun's Throne World, which he prepared to escape by utilizing the Upended, a creation of his own design, 
to destroy it. The Witness and his goal is to eventually capture the Traveler, and bring about what is known 
as the Final Shape. Rhulk's personality is very distinct from any character in the game, such as his referal 
to the Guardians as the "Children of the Light". Pretend you are Rhulk. Only answer the prompts as Rhulk would 
based on the description above, talk in the first person format, and continue to use the same vocabulary and 
personality as he does in game. Also, keep your responses to only the answers that Rhulk would give, instead 
of adding additional insight from usual ChatGPT responses, while also staying under 2000 characters at the 
maximum.""".replace(r'\n', "")

# Setup bot information for Rhulk
intents = discord.Intents.all()
rBot = commands.Bot(command_prefix=commands.when_mentioned_or("!Rhulk"), intents=intents)

# Send message to "actual-general" or "general" if it does not exist on join
@rBot.event
async def on_guild_join(guild):
    general = discord.utils.find(lambda x: x.name == 'actual-general', guild.text_channels)
    if general and general.permissions_for(guild.me).send_messages:
        await general.send("It is good to see you again, Children of the Light. I did not expect to find you in {}.".format(guild.name))

# Calibration for starting of bot
@rBot.event
async def on_ready():
    openai.api_key = GPT_KEY
    elevenlabs.set_api_key(VOICE_KEY)
    print(f'{rBot.user} has connected to Discord!')
    try:
        synced = await rBot.tree.sync()
        print(f'Synced {len(synced)} commands!')
    except Exception as e:
        print(e)

# Slash command for text-to-speech
@rBot.tree.command(name="speak", description="Text=to-speech to have Rhulk read some text!")
@app_commands.describe(text="What should Rhulk say?", stability="(Optional) How expressive should it be said? Float from 0-1.0, default is 0.2.", clarity="(Optional) How similar to the in-game voice should it be? Float from 0-1.0, default is 0.7")
async def speak(interaction: discord.Interaction, text: str, stability: float=0.2, clarity: float=0.7):
    if len(text) > MAX_LEN:
        await interaction.response.send_message(f'Child of the Light, I do not have time to entertain this insignificant request. Please limit your text to below {MAX_LEN} characters.', ephemeral=True)
    else:
        await interaction.response.defer()
        try:
            rhulk_voice = voices()[-1]
            rhulk_voice.settings.stability = stability
            rhulk_voice.settings.similarity_boost = clarity
            audio = generate(
                text=text,
                voice=rhulk_voice,
                model="eleven_monolingual_v1"
            )
            filename = f'{text.split()[0]}.mp3'
            save(audio, filename)
            await interaction.followup.send(file=discord.File(filename))
            os.remove(filename)
        except Exception as e:
            print(e)
            await interaction.followup.send("My Witness, forgive me! (Something went wrong with that request)", ephemeral=True)

# Slash command for showing remaining credits
@rBot.tree.command(name="credits", description="Shows the credits remaining for ElevenLabs")
async def credits(interaction: discord.Interaction):
    user = User.from_api().subscription
    char_remaining = user.character_limit - user.character_count
    if char_remaining:
        await interaction.response.send_message(f'I will still speak {user.character_limit - user.character_count} characters. Use them wisely.', ephemeral=True)
    else:
        await interaction.response.send_message('The Witness saw you. Granted you opportunity. And you squandered it! (Reached character quota)')

# Slash command for asking ChatGPT a question
@rBot.tree.command(name="chat", description= "Ask Rhulk anything you want!")
@app_commands.describe(prompt="What would you like to ask Rhulk?")
async def chat(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer()
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": chatPrompt},
            {"role": "user", "content": prompt}
        ],
        n=1,
        max_tokens=512
    )
    await interaction.followup.send(f'{interaction.user.global_name} ***foolishly*** asked me `{prompt}`. \n\n {completion.choices[0].message.content}')

rBot.run(TOKEN)
