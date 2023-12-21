from ast import alias
import discord
from discord.ext import commands
import random

# Class that provides dice rolling
class Roller(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name = "coin", aliases = ["50/50"], help = "Flips a coin")
    async def coin(self, ctx):
        roll = random.randint(1, 2)
        if roll % 2 == 0:
            await ctx.send("Tails!")
        else:
            await ctx.send("Heads") 

    @commands.command(name = "roll", aliases = ["r"], help = "Rolls any amount of dice in NdM format where N and M are non-negative integers")
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.split('d'))
        except Exception:
            await ctx.send("Syntax error")
            return
        result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
        await ctx.send(result)

    @commands.command(name = 'rollAdv', aliases = ["ra", "adv"], help = "Roll two d20 and choose the highest")
    async def rollAdv(self, ctx):
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = max(roll1, roll2)
        msg = f"Rolled: {roll1}, {roll2}\nResult: {result}"
        await ctx.send(msg)

    @commands.command(name = 'rollDis', aliases = ["rd", "dis"], help = "Roll two d20 and choose the lowest")
    async def rollDis(self, ctx):
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = min(roll1, roll2)
        msg = f"Rolled: {roll1}, {roll2}\nResult: {result}"
        await ctx.send(msg)