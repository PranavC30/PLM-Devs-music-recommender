import json
import os
import hashlib
import datetime

USERS_FILE = "users.json"
HISTORY_FILE = "history_{username}.json"

def _hash(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = {"password": _hash(password)}
    save_users(users)
    return True, "Account created!"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found."
    if users[username]["password"] != _hash(password):
        return False, "Wrong password."
    return True, "Login successful!"

# ---- Listening History ----
def get_history_file(username):
    return f"history_{username}.json"

def load_history(username):
    f = get_history_file(username)
    if os.path.exists(f):
        with open(f, 'r') as fp:
            return json.load(fp)
    return []

def save_history_entry(username, songs, mood, genre, feedback):
    history = load_history(username)
    entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood": mood,
        "genre": genre,
        "feedback": feedback,
        "songs": [s['Song'] for s in songs]
    }
    history.append(entry)
    with open(get_history_file(username), 'w') as f:
        json.dump(history, f)

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
    for f in [get_history_file(username), f"q_table_{username}.json"]:
        if os.path.exists(f):
            os.remove(f)

# ---- Mood Journal ----
def get_journal_file(username):
    return f"journal_{username}.json"

def load_journal(username):
    f = get_journal_file(username)
    if os.path.exists(f):
        with open(f) as fp:
            return json.load(fp)
    return []

def save_journal_entry(username, mood, note):
    journal = load_journal(username)
    journal.append({
        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.datetime.now().strftime("%H:%M"),
        "mood": mood,
        "note": note
    })
    with open(get_journal_file(username), 'w') as f:
        json.dump(journal, f)
