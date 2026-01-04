import random
from discord.ext import commands
from economy import add_money, get_balance, add_achievement

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def work(self, ctx):
        earned = random.randint(10, 100)
        add_money(ctx.author.id, earned)
        add_achievement(ctx.author.id, "first_work")
        await ctx.send(f"You earned **{earned} coins**!")

    @commands.command()
    async def balance(self, ctx):
        bal = get_balance(ctx.author.id)
        add_achievement(ctx.author.id, "first_balance")
        await ctx.send(f"Your balance: **{bal} coins**")