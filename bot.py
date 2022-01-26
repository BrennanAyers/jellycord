import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='[')


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to {bot.guilds}!')


@bot.command(name='play')
async def play(context):
	await context.send('working on it, bro')

bot.run(TOKEN)
