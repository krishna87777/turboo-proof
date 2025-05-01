from pymongo import MongoClient
import hashlib
import streamlit as st
import re

# Replace with your MongoDB connection string from secrets or env variables
MONGO_URI = st.secrets.get("mongo_uri", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["user_db"]
users_collection = db["users"]


def hash_password(password):
    """Securely hash a password."""
    return hashlib.sha256(password.encode()).hexdigest()


def validate_email(email):
    """Basic email validation."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password requirements:
    - At least 8 characters
    - Contains both letters and numbers
    """
    return len(password) >= 8 and any(c.isalpha() for c in password) and any(c.isdigit() for c in password)


def signup(username, email, password):
    """Register a new user."""
    # Input validation
    if not username or not email or not password:
        return False, "All fields are required."

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    if not validate_password(password):
        return False, "Password must be at least 8 characters and include both letters and numbers."

    # Check if username exists
    if users_collection.find_one({"username": username}):
        return False, "Username already exists."

    # Check if email exists
    if users_collection.find_one({"email": email}):
        return False, "Email already registered."

    # Create user record
    hashed_pw = hash_password(password)
    user = {
        "username": username,
        "email": email,
        "password": hashed_pw
    }
    users_collection.insert_one(user)
    return True, "User registered successfully!"


def login(username, password):
    """Authenticate a user login."""
    user = users_collection.find_one({"username": username})
    if user and user["password"] == hash_password(password):
        return True
    return False


def get_user_info(username):
    """Get user profile information."""
    user = users_collection.find_one({"username": username},
                                     {"password": 0})  # Exclude password
    return user if user else {}