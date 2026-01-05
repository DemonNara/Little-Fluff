import discord
from discord.ext import commands
from firebase import db

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_ref = db.collection("guilds").document(str(member.guild.id))
        config = guild_ref.get().to_dict() or {}

        channel_id = config.get("welcome_channel")
        role_ids = config.get("default_roles", [])

        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if channel:
                await channel.send(f"Welcome {member.mention}!")

        for role_id in role_ids:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def setwelcome(self, ctx, channel: discord.TextChannel):
        db.collection("guilds").document(str(ctx.guild.id)).set(
            {"welcome_channel": str(channel.id)}, merge=True
        )
        await ctx.send("Welcome channel set.")

async def setup(bot):
    await bot.add_cog(Welcome(bot))