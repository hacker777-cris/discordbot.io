import discord
from discord.ext import commands
from dotenv import load_dotenv
from typing import Final
import os
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer

load_dotenv()

token: Final[str] = os.getenv("CHATBOT_TOKEN")

# Initialize the Discord client
bot = commands.Bot(command_prefix='!')

# Initialize ChatterBot
chatbot = ChatBot('MyChatBot')
trainer = ChatterBotCorpusTrainer(chatbot)
trainer.train("chatterbot.corpus.english")  # Train the chatbot using English corpus

# Event listener for when the bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Event listener for when a message is received
@bot.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == bot.user:
        return

    # Get response from ChatterBot
    response = chatbot.get_response(message.content)

    # Send the response back to the same channel
    await message.channel.send(response)

# Run the bot
bot.run(token)
