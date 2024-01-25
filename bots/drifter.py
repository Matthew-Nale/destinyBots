import os
import interactions
from dotenv import load_dotenv
from src.bot import Bot
from interactions import slash_command, slash_option, OptionType

#? Initializations and global values

load_dotenv()
DRIFTER_TOKEN = os.getenv('DISCORD_TOKEN_DRIFTER')
DRIFTER_VOICE_KEY = os.getenv('ELEVEN_TOKEN_DRIFTER')

#? Drifter Bot Commands

class DrifterBot:
    
    client = Bot(
        _name="Drifter",
        _discord_token=DRIFTER_TOKEN,
        _status_messages={
            'credits': 'Ooooh, you hate to see that one!',
            'reset': "Scanning bio-metrics, AHHHH I\'m just kiddin\', you know you\'re authorized!!",
            'chat': {'response': 'Good ol\' {USERNAME} decided to ask me: ',
                    'error': 'It happens. Well, head on back and take the gambit again.'},
            'speak': {'too_long': 'Brother, we don\'t have time for this. Those motes are needing banked!',
                    'error': 'Hey, don\'t feel too bad. The best thing about Gambit is it never ends. Look me up anytime.'}
            },
        _voice_name="The Drifter",
        _voice_key=DRIFTER_VOICE_KEY,
        _voice_model="eleven_multilingual_v2",
        _chat_prompt=("Roleplay as The Drifter from Destiny 2. Emulate his irreverent "
                    "temperament, strange behaviors, and personality. Use his phrases "
                    "such as 'Brother' when referring to other Guardians. Focus on essential "
                    "details, while omitting unnecessary ones. Respond to all prompts and "
                    "questions, while keeping answers under 750 characters."),
        _use_voice=True,
        _use_text=True
    )
    
    def __init__(self):
        self.setup_drifter_bot()

    @client.bot.listen()
    async def on_ready(self):
        await self.client.bot.load_extension("chime_in")
        await self.client.on_ready()

    @slash_command(name="drifter_speak", description="Text-to-speech to have Drifter speak some text!")
    @slash_option(name="text", description="What should Drifter say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Drifter sound? Default is 0.25", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.8", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.75", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def speak(self, ctx: interactions.SlashContext, text: str, stability: float=0.25, clarity: float=0.8, style: float=0.75):
        await self.client.voice.speak(ctx, text, stability, clarity, style)

    @slash_command(name="drifter_vc_speak", description="Text-to-speech to have Drifter speak some text in the VC!")
    @slash_option(name="text", description="What should Drifter say?", required=True, opt_type=OptionType.STRING)
    @slash_option(name="vc", description="The VC for the bot to speak in. Leave empty for your current VC.", required=False, opt_type=OptionType.STRING)
    @slash_option(name="stability", description="How stable should Drifter sound? Default is 0.25", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="clarity", description="How similar to the in-game void should it be? Default is 0.8", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    @slash_option(name="style", description="(Optional) How exaggerated should the text be read? Default is 0.75", required=False, min_value=0, max_value=1, opt_type=OptionType.NUMBER)
    async def drifter_vc_speak(self, ctx: interactions.SlashContext, text: str, vc: str="", stability: float=0.25, clarity: float=0.8, style: float=0.75):
        await self.client.voice.vc_speak(ctx, text, vc, stability, clarity, style)

    @slash_command(name="drifter_credits", description="Shows the credits remaining for ElevenLabs for The Drifter")
    async def drifter_credits(self, ctx: interactions.SlashContext):
        await self.client.voice.credits(ctx)

    @slash_command(name="drifter_prompt", description="Show the prompt that is used to prime the /drifter_chat command.")
    async def drifter_prompt(self, ctx: interactions.SlashContext):
        await self.client.text.prompt(ctx)

    @slash_command(name="drifter_chat", description= "Ask Drifter anything you want!")
    @slash_option(name="prompt", description="What would you like to ask Drifter?", required=True, opt_type=OptionType.STRING)
    async def chat(self, ctx: interactions.SlashContext, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
        await self.client.text.chat(ctx, prompt, temperature, frequency_penalty, presence_penalty)

    @slash_command(name="drifter_reset", description="Reset the /drifter_chat AI's memory in case he gets too far gone")
    async def drifter_reset(self, ctx: interactions.SlashContext):
        await self.client.text.reset(ctx)

    def setup_drifter_bot(self):
        self.client.bot.add_listener(self.on_ready)
        self.client.bot.add_interaction(self.speak)
        self.client.bot.add_interaction(self.drifter_vc_speak)
        self.client.bot.add_interaction(self.drifter_credits)
        self.client.bot.add_interaction(self.drifter_prompt)
        self.client.bot.add_interaction(self.chat)
        self.client.bot.add_interaction(self.drifter_reset)