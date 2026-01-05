import discord
from discord.ext import commands
from firebase import db
from datetime import datetime

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def log(self, guild_id, action, executor, target):
        db.collection("logs").add({
            "guild_id": guild_id,
            "action": action,
            "executor": executor,
            "target": target,
            "timestamp": datetime.utcnow()
        })

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        self.log(ctx.guild.id, "kick", ctx.author.id, member.id)
        await ctx.send(f"{member} kicked.")

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        self.log(ctx.guild.id, "ban", ctx.author.id, member.id)
        await ctx.send(f"{member} banned.")

async def setup(bot):
    await bot.add_cog(Admin(bot))