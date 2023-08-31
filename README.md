# Discord Bots for Destiny Characters!

## What is this?

After having a pretty good cloned voice of the character Rhulk from the game Destiny 2 using ElevenLabs, I had a sudden thought in bed: "Could I make a bot that acts as Rhulk for Discord?"
And the answer was "Yes!". And surprisingly simple as well. After messing around with a few extra commands, eventually the Rhulk bot was born! And not long after, the Calus bot was as well!

## But... what do they do?

Good question! While some features are still missing, incomplete, or simply broken, these two bots will act and function as the characters they are named after. 
They have numerous commands each that interact with various AI APIs. Currently, interaction with ElevenLabs and OpenAI/ChatGPT is fully implemmented, with future improvements
for various features and additions being added as well.

## Sounds great! But what are the commands, and how do I use them?

Another great question! To use the bots, they are almost always being run on GCloud, so you'll need to have the bot be invited to your server. Due to cost restraints, it might not be possible to
have the main bot be invited to your server, but there are other options! By creating your own Rhulk/Calus bot, you will be able to use the discord_bots.py script for them as well! Just be sure to add
all required API keys and Discord bot keys to make sure they function correctly.

Currently, the required keys include: the generic Discord bot keys for Rhulk and Calus, your personal OpenAI key, and an ElevenLabs key for Rhulk and Calus.

And for all the available commands for the bots: 




## Rhulk, Disciple of the Witness

### */rhulk_speak*

  This allows the Rhulk bot to speak a provided text prompt, and send a .mp3 to the text channel that plays the spoken line. Additional parameters are available for increasing/decreasing the stability
  and clarity of the message. Do note, that ElevenLabs will always charge characters for this command, even when attempting to mess around with the additional parameters.

### */rhulk_vc_speak*

  This allows the Rhulk bot to join a voice channel, play a .mp3 similar to the /rhulk_speak command, then diconnect and send the same .mp3 to the text chat for future use. By default, this command assumes
  that the user is in a voice chat, and will join the same one as the user. If not, an optional "vc" parameter is available, which allows you to specify a voice channel for the bot to join and perform it's
  operations.

### */rhulk_credits*

  This allows the Rhulk bot to show the remaining characters that are available through the ElevenLabs API. Once the balance hits zero, any /rhulk_speak command will automatically fail, and an error
  message will be returned instead of the .mp3 file.

### */rhulk_chat*

  This allows the Rhulk bot to interact with ChatGPT to generate a response to a prompt that fits the character. The Rhulk bot can remember at least the most recent response at the worst, and around 
  15 responses or so at best currently. Additional parameters can be included to change the temperature, frequency_penalty, and presence_penalty, all of which can make the output more or less random when 
  needed.

### */rhulk_prompt*

  This provided an ephemeral message to the user that gives the prompt used in the /rhulk_chat command. This can then be used with ChatGPT in order to generate new responses at no cost.

### */rhulk_reset*

  This resets the Rhulk bot's memory of the server's interaction. In case the bot becomes ilegible or very broken, this command can be used to fix him.

### */rhulk_topics*

  View the list of Random Topics that can happen between the other bots. Provides the same functionality as /calus_topics.

### */rhulk_add_topic*

  Adds a new topic to the Random Topics, causing the daily random conversation to potentially be the topic. Provides the same functionality as /calus_add_topic.

### */rhulk_start_conversation*

  Causes Rhulk to start a conversation with the other bots. An optional parameter is available to specify a topic, otherwise a random topic is chosen from the Random Topics list.




## Emperor Calus

### */calus_speak*

  This allows the Calus bot to speak a provided text prompt, and send a .mp3 to the text channel that plays the spoken line. Additional parameters are available for increasing/decreasing the stability
  and clarity of the message. Do note, that ElevenLabs will always charge characters for this command, even when attempting to mess around with the additional parameters.

### */calus_vc_speak*

  This allows the Calus bot to join a voice channel, play a .mp3 similar to the /calus_speak command, then diconnect and send the same .mp3 to the text chat for future use. By default, this command assumes
  that the user is in a voice chat, and will join the same one as the user. If not, an optional "vc" parameter is available, which allows you to specify a voice channel for the bot to join and perform it's
  operations.

### */calus_credits*

  This allows the Calus bot to show the remaining characters that are available through the ElevenLabs API. Once the balance hits zero, any /calus_speak command will automatically fail, and an error
  message will be returned instead of the .mp3 file.

### */calus_chat*

  This allows the Calus bot to interact with ChatGPT to generate a response to a prompt that fits the character. The Calus bot can remember at least the most recent response at the worst, and around 
  15 responses or so at best currently. Additional parameters can be included to change the temperature, frequency_penalty, and presence_penalty, all of which can make the output more or less random when 
  needed.

### */calus_prompt*

  This provided an ephemeral message to the user that gives the prompt used in the /calus_chat command. This can then be used with ChatGPT in order to generate new responses at no cost.

### */reset_calus*

  This resets the Calus bot's memory of the server's interaction. In case the bot becomes ilegible or very broken, this command can be used to fix him.


  
