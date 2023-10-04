import sys
import asyncio
from datetime import datetime

from src.conversations import scheduledBotConversation

from bots.rhulk import rhulk
from bots.calus import calus
from bots.drifter import drifter
from bots.nezarec import nezarec
from bots.tower_pa import tower_pa

#? Running bots

async def get_tasks(bot_list:dict):
    tasks = []
    
    for name in bot_list:
        sys.stdout.write(f'Activate {name}? [Y/n] ')
        chosen = input().lower()
        
        if chosen == "y" or chosen == "":
            tasks.append(bot_list[name])
            
    sys.stdout.write('Enable daily bot conversations? [Y/n] ')
    chosen = input().lower()
    if chosen == "y" or chosen == "":
        tasks.append(scheduledBotConversation.start())

    return tasks

async def shutdown_bots():
    await rhulk.bot.close()
    await calus.bot.close()
    await drifter.bot.close()
    await nezarec.bot.close()
    await tower_pa.bot.close()
    
async def main():
    #* Create log.txt and provide date of creation
    log = open("log.txt", "w")
    log.write(f'Started bots at {datetime.now()}\n\n')
    log.close()

    #* Make dict of bots and names
    bot_list = {rhulk.name: rhulk.bot.start(rhulk.discord_token),
                calus.name: calus.bot.start(calus.discord_token),
                drifter.name: drifter.bot.start(drifter.discord_token),
                nezarec.name: nezarec.bot.start(nezarec.discord_token),
                tower_pa.name: tower_pa.bot.start(tower_pa.discord_token)}
    
    #* Ask user for which bots/events to run
    tasks = await get_tasks(bot_list)

    #* Run required tasks until canceled
    sys.stdout.write('Running chosen bots/tasks...\n')
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        sys.stdout.write('Disabling all running bots!\n')
        await shutdown_bots()

if __name__ == "__main__":
    asyncio.run(main())