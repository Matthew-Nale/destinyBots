import sys
import asyncio
from datetime import datetime

from src.conversations import scheduledBotConversation

from bots.rhulk import RhulkBot
from bots.calus import CalusBot
from bots.drifter import DrifterBot
from bots.nezarec import NezarecBot
from bots.tower_pa import TowerBot

#? Running bots

async def get_tasks(bot_list:dict) -> (list):
    """
    Get all tasks to be run from prompting user
    
    :param bot_list (dict): Dictionary of bots and bot start coroutines
    
    :return list: List of coroutines to run
    """
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

async def shutdown_bots(bots) -> (None):
    """
    Disconnects all bots from Discord
    """
    for b in bots:
        b.bot.close()
    
async def main() -> (None):
    #* Create log.txt and provide date of creation
    log = open("log.txt", "w")
    log.write(f'Started bots at {datetime.now()}\n\n')
    log.close()

    #* Make dict of bots and names
    bot_list = {'Rhulk': RhulkBot,
                'Calus': CalusBot,
                'Drifter': DrifterBot,
                'Nezarec': NezarecBot,
                'Tower PA': TowerBot}
    
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