from firebase import get_user, save_user

def add_money(user_id, amount):
    user = get_user(user_id)
    user["balance"] += amount
    save_user(user_id, user)

def get_balance(user_id):
    return get_user(user_id)["balance"]

def add_achievement(user_id, achievement):
    user = get_user(user_id)
    if achievement not in user["achievements"]:
        user["achievements"][achievement] = True
        save_user(user_id, user)