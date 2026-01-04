import random
from firebase import get_user, save_user

def xp_needed(level):
    return level * 100

def add_xp(user_id):
    user = get_user(user_id)
    gained = random.randint(1, 10)
    user["xp"] += gained

    if user["xp"] >= xp_needed(user["level"] + 1):
        user["xp"] = 0
        user["level"] += 1
        leveled = True
    else:
        leveled = False

    save_user(user_id, user)
    return leveled, user["level"]