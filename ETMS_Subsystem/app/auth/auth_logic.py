import bcrypt
import json
from functools import wraps
from flask import session, redirect, url_for

# Path to the user data file
USER_FILE = "app/auth/users.json"

def load_users():
    """Load user data from the JSON file."""
    with open(USER_FILE, "r") as file:
        return json.load(file)

def save_users(data):
    """Save user data to the JSON file."""
    with open(USER_FILE, "w") as file:
        json.dump(data, file, indent=4)

def register_user(username, password):
    """Register a new user."""
    users_data = load_users()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    users_data["users"].append({
        "username": username,
        "password": hashed_password.decode("utf-8"),
        "approved": False  # Default to not approved
    })
    save_users(users_data)

def authenticate_user(username, password):
    """Authenticate a user."""
    users_data = load_users()
    for user in users_data["users"]:
        if user["username"] == username:
            if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
                if user["approved"]:
                    return True
                return "not_approved"
    return False

def approve_user(username):
    """Approve a user."""
    users_data = load_users()
    for user in users_data["users"]:
        if user["username"] == username:
            user["approved"] = True
            save_users(users_data)
            return True
    return False

def deny_user(username):
    """Deny a user."""
    users_data = load_users()
    for user in users_data["users"]:
        if user["username"] == username:
            user["approved"] = False
            save_users(users_data)
            return True
    return False

def get_pending_users():
    """Get a list of unapproved users."""
    users_data = load_users()
    return [user for user in users_data["users"] if not user["approved"]]

from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    """Decorator to protect routes requiring authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:  # Check if the user is logged in
            return redirect(url_for("views.login"))  # Redirect to login if not logged in
        return f(*args, **kwargs)
    return decorated_function
