import pytest
#import pytest_asyncio
from music import *

@pytest.mark.asyncio
async def test_single_youtube_url_parser():
    test = await from_url("https://www.youtube.com/watch?v=zk62uUqcNyo")
    assert test.title == "System of a Down - Aerials (Remastered 2021)"

@pytest.mark.asyncio
async def test_youtube_playlist_parser():
    test = await from_url("https://www.youtube.com/playlist?list=PLaDrN74SfdT7Ueqtwn_bXo1MuSWT0ji2w")
    assert len(test) == 29
    assert test[0].title == "Solving the Zelda Timeline in 15 Minutes | Unraveled"
    assert test[28].title == "Pokemon Edibility | Unraveled"





# Helper method to create a bot
# def bot_create():
#     description = '''A Discord bot meant to assist in running virtual TTRPG sessions'''
#     intents = discord.Intents.default()
#     intents.message_content = True

#     bot = commands.Bot(command_prefix = '/', description = description, intents = intents)
#     asyncio.run(setup(bot))
#     bot.run(os.environ.get('TOKEN'))