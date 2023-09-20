import asyncio
from datetime import datetime
from src.conversations import scheduledBotConversation
from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter

#? Running bots

async def main():
    #* Create log.txt and provide date of creation
    log = open("log.txt", "w")
    log.write(f'Started bots at {datetime.now()}\n\n')
    log.close()


    #* Run bots until manually quit
    await asyncio.gather(
        calus.bot.start(calus.discord_token),
        rhulk.bot.start(rhulk.discord_token),
        drifter.bot.start(drifter.discord_token),
        scheduledBotConversation.start(),
    )

if __name__ == "__main__":
    asyncio.run(main())