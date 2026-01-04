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