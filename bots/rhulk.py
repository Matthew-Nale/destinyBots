import os
import interactions
from dotenv import load_dotenv
from src.bot import Bot
from interactions import slash_command, slash_option, OptionType

#? Initializations and global values

load_dotenv()
RHULK_TOKEN = os.getenv('DISCORD_TOKEN_RHULK')
RHULK_VOICE_KEY = os.getenv('ELEVEN_TOKEN_RHULK')

#? Rhulk Bot Commands

class RhulkBot:
    
    client = Bot(
        _name='Rhulk',
        _discord_token=RHULK_TOKEN,
        _status_messages={
            'credits': 'The Witness saw you, granted you opportunity, and yet you squandered it!',
            'reset': 'The defiant... subjugated. Not for pleasure, nor glory... but in service of an ailing, endless void. Where does your purpose lie {USERNAME}?',
            'chat': {'response': '{USERNAME} ***foolishly*** asked me: ',
                    'error' : 'I... do not know what to say to that, little one.'},
            'speak': {'too_long': 'Child of the Light, I do not have time to entertain this insignificant request.',
                    'error': 'My Witness, forgive me!'}
            },
        _voice_name="Rhulk, Disciple of the Witness",
        _voice_key=RHULK_VOICE_KEY,
        _voice_model="eleven_english_v2",
        _chat_prompt=("Roleplay as Rhulk, the Disciple of the Witness from Destiny 2 and "
                    "antagonist to the Light and Guardians. Emulate his personality, use phrases "
                    "like 'Children of the Light' and 'My Witness.' Focus on essential details, avoid "
                    "unnecessary information about Darkness and Light unless essential. Respond to all user "
                    "prompts and questions, while keeping responses under 1000 characters."),
        _use_voice=True,
        _use_text=True
    )
    
    def __init__(self):
        return self.setup_rhulk_bot()
    
    @client.bot.listen()
    async def on_ready(self):
        await self.client.bot.load_extension("chime_in")
        await self.client.on_ready()

    @slash_command(name="rhulk_speak", description="Text-to-speech to have Rhulk speak some text!")
    @slash_option(name="text", description="What should Rhulk say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Rhulk sound? Default is 0.2", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.7", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.1", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def speak(self, ctx: interactions.SlashContext, text: str, stability: float=0.2, clarity: float=0.7, style: float=0.1):
        await self.client.voice.speak(ctx, text, stability, clarity, style)

    @slash_command(name="rhulk_vc_speak", description="Text-to-speech to have Rhulk speak some text in the VC!")
    @slash_option(name="text", description="What should Rhulk say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="vc", description="The VC for the bot to speak in. Leave empty for your current VC.", required=False, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Rhulk sound? Default is 0.2", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.7", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.1", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def rhulk_vc_speak(self, ctx: interactions.SlashContext, text: str, vc: str="", stability: float=0.2, clarity: float=0.7, style: float=0.1):
        await self.client.voice.vc_speak(ctx, text, vc, stability, clarity, style)

    @slash_command(name="rhulk_credits", description="Shows the credits remaining for ElevenLabs for Rhulk, Disciple of the Witness")
    async def rhulk_credits(self, ctx: interactions.SlashContext):
        await self.client.voice.credits(ctx)

    @slash_command(name="rhulk_prompt", description="Show the prompt that is used to prime the /rhulk_chat command.")
    async def rhulk_prompt(self, ctx: interactions.SlashContext):
        await self.client.text.prompt(ctx)

    @slash_command(name="rhulk_chat", description= "Ask Rhulk anything you want!")
    @slash_option(name="prompt", description="What would you like to ask Rhulk?", required=True, opt_type=OptionType.STRING)
    async def chat(self, ctx: interactions.SlashContext, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
        await self.client.text.chat(ctx, prompt, temperature, frequency_penalty, presence_penalty)

    @slash_command(name="rhulk_reset", description="Reset the /chat_rhulk AI's memory in case he gets too far gone")
    async def rhulk_reset(self, ctx: interactions.SlashContext):
        await self.client.text.reset(ctx)
        
    def setup_rhulk_bot(self):
        self.client.bot.add_listener(self.on_ready)
        self.client.bot.add_interaction(self.speak)
        self.client.bot.add_interaction(self.rhulk_vc_speak)
        self.client.bot.add_interaction(self.rhulk_credits)
        self.client.bot.add_interaction(self.rhulk_prompt)
        self.client.bot.add_interaction(self.chat)
        self.client.bot.add_interaction(self.rhulk_reset)