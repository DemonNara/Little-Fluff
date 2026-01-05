import discord
from discord import app_commands
from discord.ext import commands
from firebase import db

class ReactionRolesSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="reactionrole_add",
        description="Add a reaction role to a message"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def add_reaction_role(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel,
        message_id: str,
        emoji: str,
        role: discord.Role
    ):
        await interaction.response.defer(ephemeral=True)

        try:
            message = await channel.fetch_message(int(message_id))
            await message.add_reaction(emoji)
        except Exception:
            await interaction.followup.send(
                "Could not fetch message or add reaction.",
                ephemeral=True
            )
            return

        db.collection("reaction_roles").add({
            "guild_id": str(interaction.guild.id),
            "channel_id": str(channel.id),
            "message_id": message_id,
            "emoji": emoji,
            "role_id": str(role.id)
        })

        await interaction.followup.send(
            "Reaction role added successfully.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(ReactionRolesSlash(bot))