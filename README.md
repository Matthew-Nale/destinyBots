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

And here are all of the various commands used: 

<br />
<br />

### */BOT_speak*

  This allows the specified bot to speak a provided text prompt, and send a .mp3 to the text channel that plays the spoken line. Additional parameters are available for increasing/decreasing the stability
  and clarity of the message. Do note that this command will use the ElevenLabs monthly character limit to generate the audio.

### */BOT_vc_speak*

  This allows the specified bot to join a voice channel, play a .mp3 similar to the /BOT_speak command, then diconnect and send the same .mp3 to the text chat for future use. By default, this command assumes
  that the user is in a voice chat, and will join the same one as the user. If not, an optional "vc" parameter is available, which allows you to specify a voice channel for the bot to join and perform it's
  operations.

### */BOT_credits*

  This allows the specified bot to show the remaining characters that are available through the ElevenLabs API. Once the balance hits zero, any /BOT_speak or /BOT_vc_speak command will automatically fail, and an error
  message will be returned instead of the .mp3 file.

### */BOT_chat*

  This allows the specified bot to interact with ChatGPT to generate a response to a prompt that fits the character. The bot can remember the most recent response for context at the worst, and around 
  5 responses or so at best currently. Additional parameters can be included to change the temperature, frequency_penalty, and presence_penalty, all of which can make the output more or less random when 
  needed.

### */BOT_prompt*

  This provided an ephemeral message to the user that gives the prompt used in the /BOT_chat command. This can then be used with ChatGPT in order to generate new responses at no cost.

### */BOT_reset*

  This resets the specified bot's memory of the server's interaction. In case the bot becomes ilegible or very broken, this command can be used to fix it.

### */BOT_topics*

  View the list of random topics that can happen between the other bots.

### */BOT_add_topic*

  Adds a new topic to the random topics, causing the daily random conversation to potentially be the topic.

### */BOT_start_conversation*

  Causes the specified bot to start a conversation with the other bots. An optional parameter is available to specify a topic, otherwise a random topic is chosen from the random topics list.

<br />
<br />

## Bot Command Compatability

| Command                  | Rhulk    | Calus    |
|--------------------------|----------|----------|
| /BOT_speak               |  &check; |  &check; 
| /BOT_vc_speak            |  &check; |  &check;
| /BOT_credits             |  &check; |  &check;
| /BOT_chat                |  &check; |  &check;
| /BOT_prompt              |  &check; |  &check;
| /BOT_reset               |  &check; |  &check;
| /BOT_topics              |  &check; |  &check;
| /BOT_add_topic           |  &check; |  &check;
| /BOT_start_conversation  |  &check; |  

<br />
<br />

## Timed Events

### Memory Cleaning Functions

  There are two seperate memory cleaning functions for the /BOT_chat commands. Whenver a bot is not interacted with in a specific time (currently 6 hours), all memories will be refreshed. The main purpose of this
  is to reduce the overall cost of the API calls.

### Daily Conversation Topic

  Everyday at 1 PM (Eastern Time), the bots will have a conversation with each other. The topic is chosen randomly from the list in 'topics.txt', and will be printed to a specific channel. Currently this channel is a
  specific named one, so be sure to change the server name and text channel name when using it outside of the main bots.
