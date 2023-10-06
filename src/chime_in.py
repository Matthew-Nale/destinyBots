import openai
import random
from src.bot import Bot, CHAT_MODEL
from discord import Message
from discord.ext import commands

from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter
from bots.nezarec import nezarec

RANDOM_CHANCE = 0.025

#? Helper Functions

async def generate_response(chosen_speaker: Bot, user_msgs: list) -> (str | Exception):
    """
    Generates a response to a single user message
    
    :param chosen_speaker (Bot): The bot that is to send the message
    :param user_msgs (list): The list of 5 most recent discord.Messages

    :return (str): Message to send in response
    """
    try:
        messages = [{"role": "system", "content": "You are in a Discord server, and will be provided with a series of messages you want to respond to. Only respond in character. " + chosen_speaker.text.chat_prompt}]
        for msg in user_msgs:
            messages.append({"role": "user", "content": msg.content})
            
        completion = openai.ChatCompletion.create(
                model=CHAT_MODEL,
                messages=messages,
                n=1,
                max_tokens=512,
                temperature=1.2,
                frequency_penalty=0.9,
                presence_penalty=0.75
            )
        return completion.choices[0].message.content
    except Exception as e:
        return e


#? Random Chime-In messages Cog

class ChimeEvents(commands.Cog):
    
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: Message) -> (None):
        """
        Event that triggers on messages, potentially having a bot send a reply
        
        :param self (Self@ChimeEvents): Self reference to ChimeEvents class
        """
        print('Triggered chime-in')
        if not message.author.bot and not message.attachments:
            if random.random() <= RANDOM_CHANCE:
                log = open("log.txt", "a")
                chosen_speaker = random.choice([b for b in [rhulk, calus, drifter, nezarec] if b.bot.is_ready()])
                past_messages = [m async for m in message.channel.history(limit=5)]
                past_messages.reverse()
                response = await generate_response(chosen_speaker, past_messages)
                await chosen_speaker.bot.get_channel(message.channel.id).send(response, reference=message)
                log.write(f'Chiming-in on previous messages {[msg.content for msg in past_messages]} with bot: {chosen_speaker.name}.\nResponse: {response}\n\n')
                log.close()
        await self.bot.process_commands(message)

async def setup(bot: Bot) -> (None):
    """
    Setup for ChimeEvents Cog

    :param bot (Bot): Bot for ChimeEvents to be enabled on
    """
    await bot.add_cog(ChimeEvents(bot))