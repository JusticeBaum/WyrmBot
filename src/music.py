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
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn',
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Source(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volume = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        
# Class that provides music player functionality
class Player(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.is_paused = False
        # Text channel the bot last received a message on
        self.tc = None
        # Current voice channel the bot occupies
        self.vc = None
        # Queue of streamable objects
        self.queue = []
        # Currently playing object
        self.cur = None

    # Helper methods

    # Returns a 'Source' object from a youtube url
    async def from_url(self, url, loop = None):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))

        # If playlist
        if 'entries' in data:
            # for each song in playlist
            for song in data['entries']:
                self.queue.append(Source(discord.FFmpegPCMAudio(song['url'], **ffmpeg_options), data=data))
                await self.tc.send("Added contents of playlist to queue")
        else:
            self.queue.append(Source(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data))
            await self.tc.send(f'Added: {self.queue[len(self.queue) - 1].title} to queue')

    # Resets the state of the queue        
    async def q_reset(self):
        self.queue = []
        self.q_index = 0

    # Bot commands

    @commands.command(name = "add", alias = ['a', '+'], help = "Add a song to the queue")
    async def add(self, ctx, url):
        await self.from_url(url, loop = self.bot.loop)

    @commands.command(name = "clear", help = 'Clear the current queue')
    async def clear(self, ctx):
        self.queue = []
        self.q_index = 0

    @commands.command(name = "join", aliases = ["j", "move"], help = "Joins caller's current voice channel")
    async def join(self, ctx):
        self.tc = ctx.channel
        channel = ctx.message.author.voice.channel
        try:
            # If this is first time joining this run
            if self.vc == None:
                self.vc =  await channel.connect()
                return
            # If moving to a different channel
            elif self.vc.is_connected():
                await ctx.voice_client.disconnect()
                self.vc = await channel.connect()
                return
        except Exception:
            await ctx.send("Caller must be in a voice channel")
            return
    
    @commands.command(name = "leave", alias = ["go"], help = "Disconnects from current voice channel")
    async def leave(self, ctx):
        self.tc = None
        self.vc = None
        self.q_reset()
        await ctx.voice_client.disconnect()

    @commands.command(name = "playing", help = "Displays information on the currently playing track")
    async def playing(self, ctx):
        if self.cur is None:
            await self.tc.send("No song currently playing")
        else:
            await self.tc.send(f'Currently playing: {self.cur.title}')

    @commands.command(name = "pause", alias = ["stop"], help = "Halt the currently playing track")
    async def pause(self, ctx):
        self.is_paused = True
        self.vc.pause()

    @commands.command(name = "play", alias = ['p'], help = "Loops through the current queue, playing each track")
    async def play(self, ctx):
            # TODO add optional *args for passing urls directly into command
            if self.is_paused:
                self.vc.resume()
            elif self.queue:
                self.is_paused = False
                play = self.queue.pop(0)
                self.cur = play
                self.vc.play(play, after=lambda e: print(f'Player error: {e}') if e else self.play_next())
            else:
                await self.tc.send("No songs in queue")

    def play_next(self):
        if self.queue:
            play = self.queue.pop(0)
            self.cur = play
            self.vc.play(play, after=lambda e: print(f'Player error: {e}') if e else self.play_next())
        else:
            print("No songs remaining in queue")
            return

    @commands.command(name = "queue", alias = ['q', "display"], help = "Displays all songs currently in the queue")
    async def queue(self, ctx):
        queue = ""
        for song in self.queue:
            queue += song.title
            queue += "\n"
        await ctx.send(queue)
            
    @commands.command(name = 'skip', help = 'Skips to the next song in the queue')
    async def skip(self, ctx):
        if self.queue:
            self.vc.pause()
            play = self.queue.pop(0)
            self.cur = play
            self.vc.play(play, after=lambda e: print(f'Player error: {e}') if e else self.play_next())
        else:
            self.vc.pause()
            await self.tc.send("No songs remaining in queue")  
    