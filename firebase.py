import firebase_admin
from firebase_admin import db

ref = None

def get_ref():
    global ref
    if ref is None:
        ref = db.reference()
    return ref

def get_user(user_id):
    ref = get_ref()
    user = ref.child("users").child(str(user_id)).get()
    if not user:
        user = {
            "xp": 0,
            "level": 1,
            "balance": 0,
            "achievements": {}
        }
        ref.child("users").child(str(user_id)).set(user)
    return user

def save_user(user_id, data):
    ref = get_ref()
    ref.child("users").child(str(user_id)).update(data)



    guilds/{guild_id}/automod/
  enabled: true
  max_messages: 5
  interval_seconds: 7
  max_caps_percent: 70
  max_links: 2
  warn_threshold: 3
  timeout_minutes: 10
  blacklist: ["badword1", "badword2"]




warnings/{guild_id}_{user_id}/
  count: int
  last_warning: timestamp


  guilds → YOUR_GUILD_ID → automod → config



  "enabled": true,
  "max_messages": 5,
  "interval_seconds": 7,
  "max_caps_percent": 70,
  "max_links": 2,
  "warn_threshold": 3,
  "timeout_minutes": 10,
  "blacklist": ["badword", "slur"]
