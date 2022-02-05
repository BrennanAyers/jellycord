import asyncio
import os
import uuid

import discord
import youtube_dl
from discord.ext import commands
from dotenv import load_dotenv
from jellyfin_apiclient_python import JellyfinClient

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
JELLYFIN_USERNAME = os.getenv('JELLYFIN_USERNAME')
JELLYFIN_PASSWORD = os.getenv('JELLYFIN_PASSWORD')
JELLYFIN_URL = os.getenv('JELLYFIN_URL')


async def send_user_not_in_vc_error(context):
	await context.send('You have to be in a vc, dork')
	raise commands.CommandError("User was not in a voice channel")


async def send_user_in_wrong_vc_error(context):
	await context.send('You have to be in the right channel, nerd')
	raise commands.CommandError("User was in a different voice channel")

ytdl_options = {
	'format': 'bestaudio/best',
	'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
}

ytdl = youtube_dl.YoutubeDL(ytdl_options)


class YoutubeStreamer(discord.PCMVolumeTransformer):
	def __init__(self, source,  *, data, volume=1.0):
		super().__init__(source, volume)

		self.data = data
		self.title = data.get('title')
		self.url = data.get('url')

	@classmethod
	async def from_url(cls, url, *, loop=None):
		loop = loop or asyncio.get_event_loop()
		data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

		return cls(discord.FFmpegPCMAudio(data['url'], options='-vn'), data=data)


jellyfin_client = JellyfinClient()
jellyfin_client.config.app('Jellycord', '1.0', 'discord', str(uuid.uuid4()))
jellyfin_client.config.data["auth.ssl"] = True
jellyfin_client.auth.connect_to_address(JELLYFIN_URL)
jellyfin_client.auth.login(JELLYFIN_URL, JELLYFIN_USERNAME, JELLYFIN_PASSWORD)
jellyfin_client.authenticate({'Servers': [jellyfin_client.auth.credentials.get_credentials()['Servers'][0]]}, discover=False)


class Jellycord(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(name='play')
	async def play(self, context, *query: str):
		concat_query = " ".join(query)
		results = jellyfin_client.jellyfin.user_items(params={'searchTerm': concat_query, 'IncludePeople': False, 'IncludeMedia': True, 'IncludeGenres': False,
            'IncludeStudios': False, 'IncludeArtists': False, 'IncludeItemTypes': 'Audio', 'Limit': 24, 'Recursive': True,
            'EnableTotalRecordCount': False, 'ImageTypeLimit': 1})
		truncated = [result['Name'] for result in results['Items']]
		await context.send(f'results: {str(truncated)}')

	@commands.command(name='url')
	async def url(self, context, *, url: str):
		async with context.typing():
			streamer = await YoutubeStreamer.from_url(url, loop=self.bot.loop)
			context.voice_client.play(streamer, after=lambda error: print(f'Player error: {error}') if error else None)

		await context.send(f'Now Playing: {streamer.title}')

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
	@url.before_invoke
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
bot.run(DISCORD_TOKEN)
