import asyncio
import discord
from discord.ext import commands
import youtube_dl

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0', 
}

ffmpeg_options = {
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Source(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volume = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    # Get a streamable object from a url
    async def from_url(cls, url, loop = None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        # if playlist
        if 'entries' in data:
            # take first item
            data = data['entries'][0]
        
        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        
# Class that provides music player functionality
class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "join", aliases = ["j"], help = "Joins caller's current voice channel")
    async def join(self, ctx):

        channel = ctx.message.author.voice.channel
        try:
            await channel.connect()
        except Exception:
            await ctx.send("Caller must be in a voice channel")
            return