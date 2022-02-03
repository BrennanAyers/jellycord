import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')


async def send_user_not_in_vc_error(context):
	await context.send('You have to be in a vc, dork')
	raise commands.CommandError("User was not in a voice channel")


async def send_user_in_wrong_vc_error(context):
	await context.send('You have to be in the right channel, nerd')
	raise commands.CommandError("User was in a different voice channel")


class Jellycord(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='play')
	async def play(self, context, *query: str):
		concat_query = " ".join(query)
		await context.send(f'searching for {str(concat_query)}, eh')

	@commands.command(name='join')
	async def join(self, context):
		requester = context.message.author
		if context.me.voice is not None:
			await context.send(f'I am already in {context.me.voice.channel}!')
		elif requester.voice is not None:
			channel = requester.voice.channel
			await channel.connect()
		else:
			await context.send('You have to be in a vc, dumbass')

	@commands.command(name='leave')
	async def leave(self, context):
		if context.me.voice is not None:
			if context.author.voice is not None:
				if context.author.voice.channel != context.me.voice.channel:
					await send_user_in_wrong_vc_error(context)
				else:
					await context.voice_client.disconnect()
			else:
				await send_user_not_in_vc_error(context)

	@play.before_invoke
	async def check_voice_client(self, context):
		if context.voice_client is None:
			if context.author.voice:
				await context.author.voice.channel.connect()
			else:
				await send_user_not_in_vc_error(context)
		elif context.author.voice is None:
			await send_user_not_in_vc_error(context)
		elif context.author.voice.channel != context.me.voice.channel:
			await send_user_in_wrong_vc_error(context)


bot = commands.Bot(command_prefix='[')


@bot.event
async def on_ready():
	print(f'{bot.user} has connected to {bot.guilds}!')


bot.add_cog(Jellycord(bot))
bot.run(TOKEN)
