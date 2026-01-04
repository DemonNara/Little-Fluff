import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://YOUR_PROJECT.firebaseio.com"
})

ref = db.reference()

def get_user(user_id):
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
    ref.child("users").child(str(user_id)).update(data)