import asyncio
import discord
from discord.ext import commands
from enum import Enum, auto, unique
import yt_dlp as youtube_dl
from urllib.parse import urlparse

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': True,
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
# ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class Source(discord.PCMVolumeTransformer):
    def __init__(self, source, data, volume = 0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

# Returns an instance of a 'Source' object
# Returns array thereof if multiple tracks are found
async def from_url(url, loop = None):
    domain = find_domain(url)
    match domain:
        case Domain.YOUTUBE:
            with youtube_dl.YoutubeDL(ytdl_format_options) as ytdl:
                data = ytdl.extract_info(url, download=False)
            result = []

            if 'entries' in data:
                print("playlist!")
                #print(list(data.items()))
                for song in data['entries']:
                    print(song['title'])
                    result.append(Source(discord.FFmpegPCMAudio(song['url'], **ffmpeg_options), data=data))
                    result[-1].title = song['title']
            else:
                result = Source(discord.FFmpegPCMAudio(data['url'], **ffmpeg_options), data=data)

            return result
        case Domain.SPOTIFY:
            #TODO
            pass
        
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

    # Bot commands

    @commands.command(name = "add", alias = ['a', '+'], help = "Add a song to the queue")
    async def add(self, ctx, url):
        to_add = await from_url(url, loop = self.bot.loop)
        if isinstance(to_add, list):
            #TODO
            self.queue += to_add
            for song in to_add:
                await self.tc.send(f"Added {song.title} to queue")
        else:
            self.queue.append(to_add)
            await self.tc.send(f"Added {to_add.title} to queue")

    @commands.command(name = "clear", help = 'Clear the current queue')
    async def clear(self, ctx):
        self.queue = []
        self.cur = None

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
        self.queue = []
        self.cur = None
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


@unique
class Domain(discord.Enum):
    YOUTUBE = auto()
    SPOTIFY = auto()


# Returns the appropriate domain Enum for a given url
def find_domain(url):
    split_url = urlparse(url)
    netloc = split_url.netloc
    domain = netloc.split('.')[1]
    match domain:
        case 'youtube':
            return Domain.YOUTUBE
        case 'spotify':
            return  Domain.SPOTIFY
    