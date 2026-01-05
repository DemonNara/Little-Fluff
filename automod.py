import discord
from discord.ext import commands
from firebase import db
from datetime import datetime, timedelta
import re
from collections import defaultdict

LINK_REGEX = re.compile(r"https?://")

class AutoMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.message_cache = defaultdict(list)

    def get_config(self, guild_id):
        ref = db.collection("guilds").document(str(guild_id)).collection("automod").document("config")
        doc = ref.get()
        return doc.to_dict() if doc.exists else {}

    def log_action(self, guild_id, action, user_id, reason):
        db.collection("logs").add({
            "guild_id": str(guild_id),
            "action": action,
            "target": str(user_id),
            "reason": reason,
            "timestamp": datetime.utcnow()
        })

    async def warn_user(self, member, reason, config):
        warn_ref = db.collection("warnings").document(f"{member.guild.id}_{member.id}")
        data = warn_ref.get().to_dict() or {"count": 0}

        data["count"] += 1
        data["last_warning"] = datetime.utcnow()
        warn_ref.set(data)

        await member.send(f"⚠️ Warning: {reason}")

        if data["count"] >= config.get("warn_threshold", 3):
            minutes = config.get("timeout_minutes", 10)
            until = discord.utils.utcnow() + timedelta(minutes=minutes)
            await member.timeout(until, reason="AutoMod escalation")
            self.log_action(member.guild.id, "timeout", member.id, "AutoMod escalation")

    @commands.Cog.listener()
    async def on_message(self, message):
        if (
            not message.guild
            or message.author.bot
            or message.author.guild_permissions.administrator
        ):
            return

        config = self.get_config(message.guild.id)
        if not config.get("enabled", False):
            return

        now = datetime.utcnow()

        # -------- SPAM DETECTION --------
        cache = self.message_cache[message.author.id]
        cache.append(now)
        interval = config.get("interval_seconds", 7)
        max_msgs = config.get("max_messages", 5)

        self.message_cache[message.author.id] = [
            t for t in cache if now - t < timedelta(seconds=interval)
        ]

        if len(self.message_cache[message.author.id]) > max_msgs:
            await message.delete()
            await self.warn_user(message.author, "Spamming messages", config)
            self.log_action(message.guild.id, "spam", message.author.id, "Message spam")
            return

        # -------- CAPS DETECTION --------
        if len(message.content) >= 8:
            caps = sum(1 for c in message.content if c.isupper())
            percent = (caps / len(message.content)) * 100

            if percent >= config.get("max_caps_percent", 70):
                await message.delete()
                await self.warn_user(message.author, "Excessive capital letters", config)
                self.log_action(message.guild.id, "caps", message.author.id, "Excessive caps")
                return

        # -------- LINK DETECTION --------
        links = LINK_REGEX.findall(message.content)
        if len(links) > config.get("max_links", 2):
            await message.delete()
            await self.warn_user(message.author, "Too many links", config)
            self.log_action(message.guild.id, "links", message.author.id, "Link spam")
            return

        # -------- BLACKLIST --------
        blacklist = config.get("blacklist", [])
        content_lower = message.content.lower()

        for word in blacklist:
            if word.lower() in content_lower:
                await message.delete()
                await self.warn_user(message.author, "Blacklisted language", config)
                self.log_action(message.guild.id, "blacklist", message.author.id, word)
                return