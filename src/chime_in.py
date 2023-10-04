import openai
import random
from src.bot import Bot, CHAT_MODEL
from discord import Message
from discord.ext import commands

from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter
from bots.nezarec import nezarec



RANDOM_CHANCE = 0.005


#? Random Chime-In messages Cog

class ChimeEvents(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    async def generate_response(chosen_speaker: Bot, user_msg: str):
        try:
            completion = openai.ChatCompletion.create(
                    model=CHAT_MODEL,
                    messages=[{"role": "system", "content": chosen_speaker.text.chat_prompt},
                            {"role": "user", "content": user_msg}],
                    n=1,
                    max_tokens=512,
                    temperature=1.2,
                    frequency_penalty=0.9,
                    presence_penalty=0.75
                )
            
            return completion.choices[0].message.content
        except Exception as e:
            return e

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            if random.random() < RANDOM_CHANCE:
                chosen_speaker = random.choice([rhulk, calus, drifter, nezarec])
                response = self.generate_response(chosen_speaker, message.content)
                await chosen_speaker.bot.get_channel(message.channel).send(response, reference=message)

def setup(bot):
    bot.add_cog(ChimeEvents(bot))