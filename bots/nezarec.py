import os
import interactions
from dotenv import load_dotenv
from src.bot import Bot
from interactions import slash_command, slash_option, OptionType

#? Initializations and global values

load_dotenv()
NEZAREC_TOKEN = os.getenv('DISCORD_TOKEN_NEZAREC')

#? Nezarec Bot Commands

class NezarecBot:
    
    client = Bot(
        _name="Nezarec",
        _discord_token=NEZAREC_TOKEN,
        _status_messages={
            'reset': 'This prison in-between… it will shatter. But I need power…',
            'chat': {'response': 'Ohh good... {USERNAME} decided to ask me: ',
                    'error': 'It\'s a shame we can\'t entertain our conversation further...'}
            },
        _chat_prompt=("Roleplay as  Nezarec, the Final God of Pain from Destiny 2 and "
                    "Disciple of the Witness. Emulate his hunger for pain and suffering, "
                    "utter derangement, insanity, and sadistic tendencies. Focus on "
                    "essential details, while omitting unnecessary ones. Respond to all "
                    "prompts and questions, while keeping answers under 750 characters."),
        _use_voice=False,
        _use_text=True
    )
    
    def __init__(self):
        self.setup_nezarec_bot()

    @client.bot.listen()
    async def on_ready(self):
        await self.client.bot.load_extension('chime_in')
        await self.client.on_ready()

    @slash_command(name="nezarec_prompt", description="Show the prompt that is used to prime the /nezarec_chat command.")
    async def nezarec_prompt(self, ctx: interactions.SlashContext):
        await self.client.text.prompt(ctx)

    @slash_command(name="drifter_chat", description= "Ask Nezarec anything you want!")
    @slash_option(name="prompt", description="What would you like to ask Nezarec?", required=True, opt_type=OptionType.STRING)
    async def chat(self, ctx: interactions.SlashContext, prompt: str, temperature: float=1.2, frequency_penalty: float=0.9, presence_penalty: float=0.75):
        await self.client.text.chat(ctx, prompt, temperature, frequency_penalty, presence_penalty)

    @slash_command(name="nezarec_reset", description="Reset the /chat_nezarec AI's memory in case he gets too far gone")
    async def nezarec_reset(self, ctx: interactions.SlashContext):
        await self.client.text.reset(ctx)

    def setup_nezarec_bot(self):
        self.client.bot.add_listener(self.on_ready)
        self.client.bot.add_interaction(self.nezarec_prompt)
        self.client.bot.add_interaction(self.chat)
        self.client.bot.add_interaction(self.nezarec_reset)