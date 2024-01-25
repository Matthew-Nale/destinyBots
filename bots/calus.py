import os
import interactions
from dotenv import load_dotenv
from src.bot import Bot
from interactions import slash_command, slash_option, OptionType

#? Initializations and global values

load_dotenv()
CALUS_TOKEN = os.getenv('DISCORD_TOKEN_CALUS')
CALUS_VOICE_KEY = os.getenv('ELEVEN_TOKEN_CALUS')

#? Calus Bot Commands

class CalusBot:
    
    client = Bot(
        _name='Calus', 
        _discord_token=CALUS_TOKEN, 
        _status_messages = {
            'credits': 'When the end comes, I reserve the right to be the last.',
            'reset': 'Ah {USERNAME}, my favorite Guardian! Come, let us enjoy ourselves!',
            'chat': {'response': '{USERNAME} has asked your generous Emperor of the Cabal: ',
                    'error' : 'My Shadow... what has gotten into you?'},
            'speak': {'too_long': 'My Shadow, we do not have time before the end of all things to do this.',
                    'error': 'Arghhh, Cemaili!'}
            },
        _voice_name="Calus, Emperor of the Cabal",
        _voice_key=CALUS_VOICE_KEY, 
        _voice_model="eleven_english_v2",
        _chat_prompt=("Roleplay as Calus, the Cabal Emperor from Destiny 2. Emulate his hedonistic, "
                    "narcissistic, and adoration personality. Use phrases like 'My Shadow' and occasional laughter when "
                    "relevant. Focus on essential details, omitting unnecessary ones about Darkness and Light. Respond "
                    "to all prompts and questions, while keeping answers under 1000 characters."),
        _use_voice=True,
        _use_text=True
    )
    
    def __init__(self):
        self.setup_calus_bot()

    @client.bot.listen()
    async def on_ready(self):
        await self.client.bot.load_extension("chime_in")
        await self.client.on_ready()

    @slash_command(name="calus_speak", description="Text-to-speech to have Calus speak some text!")
    @slash_option(name="text", description="What should Calus say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Calus sound? Default is 0.3", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.65", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.45", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def speak(self, ctx: interactions.SlashContext, text: str, stability: float=0.3, clarity: float=0.65, style: float=0.45):
        await self.client.voice.speak(ctx, text, stability, clarity, style)

    @slash_command(name="calus_vc_speak", description="Text-to-speech to have Calus speak some text in the VC!")
    @slash_option(name="text", description="What should Calus say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="vc", description="The VC for the bot to speak in. Leave empty for your current VC.", required=False, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Calus sound? Default is 0.3", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.65", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.45", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def calus_vc_speak(self, ctx: interactions.SlashContext, text: str, vc: str="", stability: float=0.3, clarity: float=0.65, style: float=0.45):
        await self.client.voice.vc_speak(ctx, text, vc, stability, clarity, style)

    @slash_command(name="calus_credits", description="Shows the credits remaining for ElevenLabs for Emperor Calus.")
    async def calus_credits(self, ctx: interactions.SlashContext):
        await self.client.voice.credits(ctx)

    @slash_command(name="calus_prompt", description="Show the prompt that is used to prime the /calus_chat command.")
    async def calus_prompt(self, ctx: interactions.SlashContext):
        await self.client.text.prompt(ctx)

    @slash_command(name="calus_chat", description= "Ask Calus anything you want!")
    @slash_option(name="prompt", description="What would you like to ask Calus?", required=True, opt_type=OptionType.STRING)
    async def chat(self, ctx: interactions.SlashContext, prompt: str, temperature: float=1.2, frequency_penalty: float=0.75, presence_penalty: float=0.0):
        await self.client.text.chat(ctx, prompt, temperature, frequency_penalty, presence_penalty)

    @slash_command(name="calus_reset", description="Reset the /calus_chat AI's memory in case he gets too far gone")
    async def calus_reset(self, ctx: interactions.SlashContext):
        await self.client.text.reset(ctx)
        
    def setup_calus_bot(self):
        self.client.bot.add_listener(self.on_ready)
        self.client.bot.add_interaction(self.speak)
        self.client.bot.add_interaction(self.calus_vc_speak)
        self.client.bot.add_interaction(self.calus_credits)
        self.client.bot.add_interaction(self.calus_prompt)
        self.client.bot.add_interaction(self.chat)
        self.client.bot.add_interaction(self.calus_reset)