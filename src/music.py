import asyncio
import discord
from discord.ext import commands
import yt_dlp as youtube_dl

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
        # Current voice channel the bot occupies
        self.vc = None

    @commands.command(name = "join", aliases = ["j"], help = "Joins caller's current voice channel")
    async def join(self, ctx):
        channel = ctx.message.author.voice.channel
        try:
            if self.vc == None or not self.vc.is_connected():
                self.vc =  await channel.connect()
                return
        except Exception:
            await ctx.send("Caller must be in a voice channel")
            return
    
    @commands.command(name = "play", alias = ['p'], help = "Streams from a Youtube URL")
    async def play(self, ctx, url):
        player = await Source.from_url(url, loop=self.bot.loop)
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

        await ctx.send(f'Now playing: {player.title}')

    # @commands.command(name = "skip", help = "Jumps to the next song in the queue")
    # async def skip(self, ctx):

    @commands.command(name = "pause", help = "Halt the currently playing track")
    async def pause(self, ctx):
        self.vc.pause()

    @commands.command(name = "resume", help = "Resumes playing the currently paused track")
    async def resume(self, ctx):
        self.vc.resume()
    
    @commands.command(name = "stop", alias = ['s'], help = "Halts the player by disconnecting from the connected voice channel")
    async def stop(self, ctx):
        await ctx.voice_client.disconnect()
    