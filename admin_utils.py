import yaml
from pathlib import Path

USER_FILE = Path("users.yaml")

def load_users():
    with USER_FILE.open("r") as f:
        return yaml.safe_load(f)

def save_users(data):
    with USER_FILE.open("w") as f:
        yaml.dump(data, f, default_flow_style=False)

def add_user(username, password, role):
    username = username.lower()
    username = username+'@randomtrees.com'
    data = load_users()
    if username in data['credentials']['usernames']:
        return False  # user exists
    data['credentials']['usernames'][username] = {
        "password": password,
        "role": role
    }
    save_users(data)
    return True

def delete_user(username):
    data = load_users()
    if username in data['credentials']['usernames']:
        del data['credentials']['usernames'][username]
        save_users(data)
        return True
    return False

def update_password(username, new_password):
    data = load_users()
    if username in data['credentials']['usernames']:
        data['credentials']['usernames'][username]['password'] = new_password
        save_users(data)
        return True
    return False

def update_role(username, role):
    data = load_users()
    if username in data['credentials']['usernames']:
        data['credentials']['usernames'][username]['role'] = role
        save_users(data)
        return True
    return False

def list_users():
    data = load_users()
    return data['credentials']['usernames']


def reset_password(username, new_password, old_password):
    data = load_users()
    if username in data['credentials']['usernames']:
        if data['credentials']['usernames'][username]['password'] == old_password:
            data['credentials']['usernames'][username]['password'] = new_password
            save_users(data)
            return True
    return False
