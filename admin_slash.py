import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta, datetime
from firebase import db

class AdminSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def log_action(self, guild_id, action, executor_id, target_id, reason=None):
        db.collection("logs").add({
            "guild_id": str(guild_id),
            "action": action,
            "executor": str(executor_id),
            "target": str(target_id),
            "reason": reason,
            "timestamp": datetime.utcnow()
        })

    # -------- KICK --------
    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None
    ):
        await interaction.response.defer(ephemeral=True)
        await member.kick(reason=reason)

        self.log_action(
            interaction.guild.id,
            "kick",
            interaction.user.id,
            member.id,
            reason
        )

        await interaction.followup.send(
            f"{member} has been kicked.",
            ephemeral=True
        )

    # -------- BAN --------
    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str | None = None
    ):
        await interaction.response.defer(ephemeral=True)
        await member.ban(reason=reason)

        self.log_action(
            interaction.guild.id,
            "ban",
            interaction.user.id,
            member.id,
            reason
        )

        await interaction.followup.send(
            f"{member} has been banned.",
            ephemeral=True
        )

    # -------- TIMEOUT --------
    @app_commands.command(
        name="timeout",
        description="Timeout a member (minutes)"
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: int,
        reason: str | None = None
    ):
        await interaction.response.defer(ephemeral=True)

        until = discord.utils.utcnow() + timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)

        self.log_action(
            interaction.guild.id,
            "timeout",
            interaction.user.id,
            member.id,
            f"{minutes} minutes | {reason}"
        )

        await interaction.followup.send(
            f"{member} timed out for {minutes} minutes.",
            ephemeral=True
        )

    # -------- PURGE --------
    @app_commands.command(
        name="purge",
        description="Delete a number of messages from a channel"
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int
    ):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        self.log_action(
            interaction.guild.id,
            "purge",
            interaction.user.id,
            interaction.channel.id,
            f"{len(deleted)} messages"
        )

        await interaction.followup.send(
            f"Deleted {len(deleted)} messages.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(AdminSlash(bot))

    import discord
from discord import app_commands
from discord.ext import commands
from firebase_admin import firestore

db = firestore.client()

class AutoModSlash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_ref(self, guild_id):
        return (
            db.collection("guilds")
            .document(str(guild_id))
            .collection("automod")
            .document("config")
        )

    # ---------- ENABLE / DISABLE ----------

    @app_commands.command(name="automod_enable", description="Enable auto moderation")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_enable(self, interaction: discord.Interaction):
        self.get_ref(interaction.guild_id).set({"enabled": True}, merge=True)
        await interaction.response.send_message("✅ AutoMod enabled", ephemeral=True)

    @app_commands.command(name="automod_disable", description="Disable auto moderation")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_disable(self, interaction: discord.Interaction):
        self.get_ref(interaction.guild_id).set({"enabled": False}, merge=True)
        await interaction.response.send_message("❌ AutoMod disabled", ephemeral=True)

    # ---------- SPAM CONFIG ----------

    @app_commands.command(name="automod_spam", description="Configure spam detection")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_spam(
        self,
        interaction: discord.Interaction,
        max_messages: int,
        interval_seconds: int
    ):
        self.get_ref(interaction.guild_id).set({
            "max_messages": max_messages,
            "interval_seconds": interval_seconds
        }, merge=True)

        await interaction.response.send_message(
            f"✅ Spam detection set: {max_messages} messages / {interval_seconds}s",
            ephemeral=True
        )

    # ---------- CAPS CONFIG ----------

    @app_commands.command(name="automod_caps", description="Set caps percentage limit")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_caps(
        self,
        interaction: discord.Interaction,
        max_caps_percent: int
    ):
        self.get_ref(interaction.guild_id).set({
            "max_caps_percent": max_caps_percent
        }, merge=True)

        await interaction.response.send_message(
            f"✅ Caps limit set to {max_caps_percent}%",
            ephemeral=True
        )

    # ---------- LINK CONFIG ----------

    @app_commands.command(name="automod_links", description="Set max links per message")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_links(
        self,
        interaction: discord.Interaction,
        max_links: int
    ):
        self.get_ref(interaction.guild_id).set({
            "max_links": max_links
        }, merge=True)

        await interaction.response.send_message(
            f"✅ Link limit set to {max_links}",
            ephemeral=True
        )

    # ---------- WARN / TIMEOUT ----------

    @app_commands.command(name="automod_punishment", description="Configure warning escalation")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_punishment(
        self,
        interaction: discord.Interaction,
        warn_threshold: int,
        timeout_minutes: int
    ):
        self.get_ref(interaction.guild_id).set({
            "warn_threshold": warn_threshold,
            "timeout_minutes": timeout_minutes
        }, merge=True)

        await interaction.response.send_message(
            f"✅ Punishments set: {warn_threshold} warnings → {timeout_minutes} min timeout",
            ephemeral=True
        )

    # ---------- BLACKLIST ----------

    @app_commands.command(name="automod_blacklist_add", description="Add a word to the blacklist")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_blacklist_add(
        self,
        interaction: discord.Interaction,
        word: str
    ):
        ref = self.get_ref(interaction.guild_id)
        doc = ref.get().to_dict() or {}
        blacklist = set(doc.get("blacklist", []))
        blacklist.add(word.lower())

        ref.set({"blacklist": list(blacklist)}, merge=True)
        await interaction.response.send_message(f"🚫 Added `{word}` to blacklist", ephemeral=True)

    @app_commands.command(name="automod_blacklist_remove", description="Remove a word from the blacklist")
    @app_commands.checks.has_permissions(administrator=True)
    async def automod_blacklist_remove(
        self,
        interaction: discord.Interaction,
        word: str
    ):
        ref = self.get_ref(interaction.guild_id)
        doc = ref.get().to_dict() or {}
        blacklist = set(doc.get("blacklist", []))
        blacklist.discard(word.lower())

        ref.set({"blacklist": list(blacklist)}, merge=True)
        await interaction.response.send_message(f"✅ Removed `{word}` from blacklist", ephemeral=True)


async def setup(bot):
    await bot.add_cog(AutoModSlash(bot))