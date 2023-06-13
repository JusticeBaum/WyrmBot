import asyncio
import discord
from discord.ext import commands
from music import Player
from roller import Roller
import os

# add all cogs to a created bot
async def setup(bot):
    await bot.add_cog(Player(bot))
    await bot.add_cog(Roller(bot))

# Create and run the bot
def main():
    description = '''A Discord bot meant to assist in running virtual TTRPG sessions'''

    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix='/', description = description, intents = intents)
    asyncio.run(setup(bot))
    bot.run(os.environ.get('TOKEN'))

if __name__ == '__main__':
    main()

