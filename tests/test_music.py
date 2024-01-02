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
    assert test[28].title == "Pokémon Edibility | Unraveled"

def test_find_domain():
    youtube_test = find_domain("https://www.youtube.com/watch?v=zk62uUqcNyo")
    assert youtube_test is Domain.YOUTUBE

    spotify_test = find_domain("https://open.spotify.com/track/6yCysJaY0lFqHnrHvaR4pF")
    assert spotify_test is Domain.SPOTIFY