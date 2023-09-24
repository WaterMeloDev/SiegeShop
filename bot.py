import discord
import os
import asyncio
from discord import app_commands, utils
from discord.ext import commands, tasks
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', intents=intents)
client.remove_command('help')

activity = discord.Activity(type=discord.ActivityType.competing, name="Sieges • /order")

@client.event
async def on_ready():
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands!")
    except:
        print(f'Already synced')
    print(f"Connected to {client.user}!")
    try:
        await client.change_presence(activity=activity, status=discord.Status.online)
    except Exception as e:
        print(f"Error: {e}")

async def setup_cogs():
    try:
        for filename in os.listdir('cogs/'):
            if filename.endswith('.py'):
                cog_name = f'cogs.{filename[:-3]}'
                await client.load_extension(cog_name)
    except Exception as e:
        print(f"Error: {e}")

async def main():
    await setup_cogs()
    await client.start(TOKEN)

asyncio.run(main())
