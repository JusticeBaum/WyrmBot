from ast import alias
import discord
from discord.ext import commands
import random

# Class that provides dice rolling
class Roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "roll", aliases = ["r"], help = "Rolls any amount of dice in NdM format where N and M are non-negative integers")
    async def roll(ctx, dice: str):
        try:
            dice = ctx.message.content
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send("Syntax error")
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)