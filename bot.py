import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=INTENTS
        )

    async def setup_hook(self):
        # Load cogs
        await self.load_extension("cogs.welcome")
        await self.load_extension("cogs.xp")
        await self.load_extension("cogs.admin")
        await self.load_extension("cogs.reaction_roles_slash")

        # Sync slash commands globally
        await self.tree.sync()
        print("Slash commands synced")

bot = MyBot()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

bot.run(os.getenv("DISCORD_TOKEN"))