# utils/database.py

import json
import os

DB_FILE = "users.json"

def add_user(user_id):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r+") as f:
        users = json.load(f)
        if user_id not in users:
            users.append(user_id)
            f.seek(0)
            json.dump(users, f)
            f.truncate()

def get_users():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)
