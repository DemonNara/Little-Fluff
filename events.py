from discord.ext import commands
from leveling import add_xp

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        leveled, level = add_xp(message.author.id)
        if leveled:
            await message.channel.send(
                f"{message.author.mention} leveled up to **Level {level}**!"
            )

        await self.bot.process_commands(message)