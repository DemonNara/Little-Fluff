from discord.ext import tasks
from datetime import datetime
from firebase import ref

@tasks.loop(seconds=60)
async def reminder_loop(bot):
    now = datetime.now().timestamp()
    reminders = ref.child("reminders").get() or {}

    for key, reminder in reminders.items():
        if now >= reminder["time"]:
            channel = bot.get_channel(reminder["channel"])
            if channel:
                await channel.send(f'<@{reminder["user"]}> {reminder["message"]}')
            ref.child("reminders").child(key).delete()
            