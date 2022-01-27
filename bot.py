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
async def play(context, *query: str):
	concat_query = " ".join(query)
	await context.send(f'searching for {str(concat_query)}, eh')

bot.run(TOKEN)
