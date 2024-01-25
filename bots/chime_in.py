import openai
import random
import datetime
import interactions
from src.bot import Bot, CHAT_MODEL
from interactions import Extension

RANDOM_CHANCE = 0.01

#? Helper Functions

async def generate_response(chosen_speaker: Bot, user_msgs: list) -> (str):
    """
    Generates a response to a single user message
    
    :param chosen_speaker (Bot): The bot that is to send the message
    :param user_msgs (list): The list of 5 most recent discord.Messages

    :return (str): Message to send in response
    """
    try:
        messages = [{"role": "system", "content": chosen_speaker.text.chat_prompt + "  You will be provided with a series of Discord in the format NAME: MESSAGE. Respond as {}: MESSAGE.".format(chosen_speaker.name)}]
        for msg in user_msgs:
            messages.append({"role": "user", "content": "{}: {}".format(msg.author.display_name, msg.content)})

        completion = openai.ChatCompletion.create(
                model=CHAT_MODEL,
                messages=messages,
                n=1,
                max_tokens=512,
                temperature=1.3,
                frequency_penalty=0.9,
                presence_penalty=0.75
            )
        return completion.choices[0].message.content.split(': ', 1)[1]
    except Exception as e:
        return e


#? Random Chime-In messages Cog

class ChimeEvents(Extension):
    
    def __init__(self, bot: Bot):
        self.bot = bot

    @interactions.listen()
    async def on_message_create(self, message: interactions.Message) -> (None):
        """
        Event that triggers on messages, potentially having a bot send a reply
        
        :param self (Self@ChimeEvents): Self reference to ChimeEvents class
        """
        if not message.message.author.bot and not message.message.attachments:
            if random.random() <= RANDOM_CHANCE:
                log = open("log.txt", "a")
                past_messages = [m async for m in message.message.channel.history(after=datetime.datetime.now() - datetime.timedelta(hours=12), limit=5)]
                past_messages.reverse()
                response = await generate_response(self.bot, past_messages)
                log.write(f'Chiming-in on previous messages {[msg.content for msg in past_messages]} with bot: {self.bot.name}.\nResponse: {response}\n\n')
                await self.bot.bot.get_channel(message.message.channel.id).send(response, reference=message.message)
                log.close()
        await self.bot.process_commands(message)

def setup(bot) -> (None):
    """
    Setup for ChimeEvents Extension

    :param bot: Client for ChimeEvents to be enabled on
    """
    ChimeEvents(bot)