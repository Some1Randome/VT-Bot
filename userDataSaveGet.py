import json
import os

FILE = os.path.join(os.path.dirname(__file__), "UserData.json")

def load_data():
    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return {}
    
def save_data(data):
    with open(FILE, "w") as f:
        json.dump(data, f, indent=4)

def save_new_user(discord_id, username, tag):
    users = load_data()

    users[str(discord_id)] = {
        "username": username,
        "tag": tag 
    }

    save_data(users)

def get_user(discord_id):
    users = load_data()
    return users.get(str(discord_id))