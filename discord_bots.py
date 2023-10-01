import sys
import asyncio
from datetime import datetime
from src.conversations import scheduledBotConversation
from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter

#? Running bots

async def get_tasks(bot_list:dict):
    tasks = []
    
    for name in bot_list:
        sys.stdout.write(f'Activate {name}? [Y/n] ')
        if input().lower() == "y":
            tasks.append(bot_list[name])
            
    sys.stdout.write(f'Enable daily bot conversations? [Y/n] ')
    if input().lower() == "y":
        tasks.append(scheduledBotConversation.start())

    return tasks

async def main():
    #* Create log.txt and provide date of creation
    log = open("log.txt", "w")
    log.write(f'Started bots at {datetime.now()}\n\n')
    log.close()

    #* Make dict of bots and names
    bot_list = {rhulk.name: rhulk.bot.start(rhulk.discord_token),
                calus.name: calus.bot.start(calus.discord_token),
                drifter.name: drifter.bot.start(drifter.discord_token)}
    
    #* Ask user for which bots/events to run
    tasks = await get_tasks(bot_list)

    #* Run required tasks until complete
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())