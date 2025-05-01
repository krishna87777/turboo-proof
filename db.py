import streamlit as st
from pymongo import MongoClient

# Use MONGO_URI from Streamlit secrets
MONGO_URI = st.secrets["MONGO_URI"]

client = MongoClient(MONGO_URI)
db = client["turbo_proof"]
users_collection = db["users"]
projects_collection = db["projects"]
