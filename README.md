# Discord Bots for Destiny Characters!

## What is this?

After having a pretty good cloned voice of the character Rhulk from the game Destiny 2 for a while, I had a sudden thought in bed: "Could I make a bot that acts as Rhulk for Discord?"
And the answer was "Yes!". and surprisingly simple. After messing around with a few extra commands, eventually the Rhulk bot was born! And not long after, the Calus bot was as well!

## But... what do they do?

Good question! While some features are still missing, incomplete, or simply broken, these two bots will act and function as the characters they are named after. 
They have numerous commands each that interact with various AI APIs. Currently, interaction with ElevenLabs and OpenAI/ChatGPT is fully implemmented, with future improvements
to their prompt memories for ChatGPT and cloned voices from ElevenLabs being worked on.

## Sounds great! But what are the commands, and how do I use them?

Another great question! To use the bots, they are almost always being run on GCloud, so you'll need to have the bot be invited to your server. Due to cost restraints, it might not be possible to
have the main bot be invited to your server, but there are other options! By creating your own Rhulk/Calus bot, you will be able to use the discord_bots.py script for them as well! Just be sure to add
all required API keys and Discord bot keys to make sure they function correctly.

And for all the available commands for the bots: 




## * *Rhulk, Disciple of the Witness* *

### /speak_rhulk

  This allows the Rhulk bot to speak a provided text prompt, and send a .mp3 to the text channel that plays the spoken line. Additional parameters are available for increasing/decreasing the stability
  and clarity of the message. Do note, that ElevenLabs will always charge characters for this command, even when attempting to mess around with the additional parameters

### /credits

  This allows the Rhulk bot to show the remaining characters that are available through the ElevenLabs API. Once the balance hits zero, any /speak_rhulk command will automatically fail, and an error
  message will be returned instead of the .mp3 file.

### /chat_rhulk

  This allows the Rhulk bot to interact with ChatGPT to generate a response to a prompt that fits the character. The Rhulk bot can remember at least the most recent response at the worst, and around 
  15 responses or so at best currently. Additional parameters can be included to change the temperature, frequency_penalty, and presence_penalty, all of which can make the output more or less random when 
  needed.

### /prompt_rhulk

  This provided an ephemeral message to the user that gives the prompt used in the /chat_rhulk command. This can then be used with ChatGPT in order to generate new responses at no cost.

### /reset_rhulk

  This resets the Rhulk bot's memory of the server's interaction. In case the bot becomes ilegible or very broken, this command can be used to fix him.




## * *Emperor Calus* *

### /speak_calus

  This allows the Calus bot to speak a provided text prompt, and send a .mp3 to the text channel that plays the spoken line. Additional parameters are available for increasing/decreasing the stability
  and clarity of the message. Do note, that ElevenLabs will always charge characters for this command, even when attempting to mess around with the additional parameters

### /chat_calus

  This allows the Calus bot to interact with ChatGPT to generate a response to a prompt that fits the character. The Calus bot can remember at least the most recent response at the worst, and around 
  15 responses or so at best currently. Additional parameters can be included to change the temperature, frequency_penalty, and presence_penalty, all of which can make the output more or less random when 
  needed.

### /prompt_calus

  This provided an ephemeral message to the user that gives the prompt used in the /chat_calus command. This can then be used with ChatGPT in order to generate new responses at no cost.

### /reset_calus

  This resets the Calus bot's memory of the server's interaction. In case the bot becomes ilegible or very broken, this command can be used to fix him.


  
