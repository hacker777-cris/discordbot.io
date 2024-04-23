import discord
from discord.ext import commands
from pytube import YouTube
import asyncio
import os
from dotenv import load_dotenv
import tkinter as tk
from tkinter import filedialog
from typing import Final

load_dotenv()
token: Final[str] = os.getenv("TOKEN")

# Define the intents for the bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False

# Create a Discord client
client = commands.Bot(command_prefix='!', intents=intents)

# Function to fetch available video qualities
def get_video_qualities(url):
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc()
    return [f"{stream.resolution} - {stream.itag}" for stream in streams]

# Function to download YouTube video with selected quality
def download_video(url, itag):
    # Create the root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select a folder
    folder_path = filedialog.askdirectory(initialdir=os.path.expanduser("~/Desktop"), title='Select a folder')

    if folder_path:
        # Download the video to the selected folder
        yt = YouTube(url)
        stream = yt.streams.get_by_itag(itag)
        stream.download(output_path=folder_path)
    else:
        raise ValueError("No folder selected.")

@client.event
async def on_ready() -> None:
    print(f"Logged in as {client.user.name} ({client.user.id})")
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="!help"))
    print("Ready!")
    print(f"Discord.py version: {discord.__version__}")
    return

# Bot command to download video
@client.command()
async def download(ctx, url):
    await ctx.send("Fetching available qualities...")

    # Get available qualities
    qualities = get_video_qualities(url)

    if qualities:
        # Display available qualities to the user
        await ctx.send("Available qualities:")
        for quality in qualities:
            await ctx.send(quality)

        # Wait for the user to select a quality
        await ctx.send("Please enter the itag of the quality you want to download (e.g., '137'):")

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel

        try:
            # Wait for user response
            quality_message = await client.wait_for('message', check=check, timeout=60)

            # Download the video with the selected quality
            selected_itag = quality_message.content.strip()
            await ctx.send(f"Downloading video with itag {selected_itag}...")

            # Make the download process asynchronous
            await asyncio.to_thread(download_video, url, selected_itag)

            await ctx.send("Video downloaded!")
        except asyncio.TimeoutError:
            await ctx.send("You took too long to respond. Please try again.")
        except Exception as e:
            await ctx.send(f"An error occurred while downloading the video: {str(e)}")
    else:
        await ctx.send("No qualities found for this video.")

# Run the bot
client.run(token)
