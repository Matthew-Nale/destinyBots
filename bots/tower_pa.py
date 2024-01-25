import os
import json
import interactions
from dotenv import load_dotenv
from src.bot import Bot
from interactions import slash_command, slash_option, OptionType

#? Initializations and global values

load_dotenv()
TOWER_TOKEN = os.getenv('DISCORD_TOKEN_TOWER')

#? Tower Bot Commands

class TowerBot:
    
    client = Bot(
        _name="Tower",
        _discord_token=TOWER_TOKEN,
        _use_voice=False,
        _use_text=False
    )
    
    def __init__(self):
        self.setup_tower_bot()

    @client.bot.listen()
    async def on_ready(self):
        await self.client.on_ready()

    @slash_command(name="topics", description="View the saved topics that the bots can chat over!")
    async def topics(ctx: interactions.SlashContext):
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
        await ctx.send(f'Guardian, we\'ve intercepted a transmission between the other bots. They will probably talk about one of these: \n\n{response}', ephemeral=True)

    @slash_command(name="add_topic", description="Add a topic that can be used for the daily conversation!")
    @slash_option(name="topic", description="Add a topic that can be used for the daily conversation!", required=True, opt_type=OptionType.STRING)
    async def add_topic(ctx: interactions.SlashContext, topic: str=None):
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
                    await ctx.send(f'Good choice, {ctx.user.global_name}. We\'ll inform the others to talk about **{topic}** in the future.')
            else:
                await ctx.send(f'The others will already talk about that topic, {ctx.user.global_name}. (Already in list)')
        else:
            await ctx.send(f'{ctx.user.global_name}? Come in {ctx.user.global_name}! (Must input something)')
            
    def setup_tower_bot(self):
        self.client.bot.add_listener(self.on_ready)
        self.client.bot.add_interaction(self.topics)
        self.client.bot.add_interaction(self.add_topic)