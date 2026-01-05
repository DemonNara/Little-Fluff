import discord
from discord.ext import commands
import random
from firebase import db
from datetime import datetime, timedelta

XP_COOLDOWN = 30  # seconds

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_ref = db.collection("users").document(
            f"{message.guild.id}_{message.author.id}"
        )

        data = user_ref.get().to_dict() or {
            "xp": 0,
            "level": 1,
            "last_message": None
        }

        now = datetime.utcnow()
        last = data.get("last_message")

        if last and now - last < timedelta(seconds=XP_COOLDOWN):
            return

        xp_gain = random.randint(5, 15)
        data["xp"] += xp_gain
        data["last_message"] = now

        if data["xp"] >= data["level"] * 100:
            data["level"] += 1
            await message.channel.send(
                f"{message.author.mention} leveled up to **{data['level']}**!"
            )

        user_ref.set(data)

    @commands.command()
    async def rank(self, ctx):
        user_ref = db.collection("users").document(
            f"{ctx.guild.id}_{ctx.author.id}"
        ).get()

        if not user_ref.exists:
            await ctx.send("No data yet.")
            return

        data = user_ref.to_dict()
        await ctx.send(
            f"XP: {data['xp']} | Level: {data['level']}"
        )

async def setup(bot):
    await bot.add_cog(XP(bot))