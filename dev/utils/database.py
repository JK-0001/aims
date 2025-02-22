import streamlit as st
import sqlite3
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Load environment variables
load_dotenv()

# Use the key from .env
key = os.getenv('FERNET_KEY').encode()

# Initialize SQLite DB
def init_db():
    conn = sqlite3.connect('health.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS health_data (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    sleep REAL,
                    mood TEXT,
                    water INTEGER,
                    food_beverages TEXT
                )''')
    conn.commit()
    return conn

# Encrypt sensitive data (e.g., mood)
def encrypt_data(data, key):
    try:
        fernet = Fernet(key)
        # Encode the data (including emojis) to UTF-8 before encryption
        encrypted_data = fernet.encrypt(data.encode('utf-8')).decode('utf-8')
        return encrypted_data
    except Exception as e:
        st.error(f"Encryption failed: {e}")
        return data  # Return original data if encryption fails

# Decrypt sensitive data
def decrypt_data(data, key):
    try:
        fernet = Fernet(key)
        # Decode the data back to UTF-8 after decryption
        decrypted_data = fernet.decrypt(data.encode('utf-8')).decode('utf-8')
        return decrypted_data
    except Exception as e:
        st.error(f"Decryption failed: {e}")
        return data  # Return original data if decryption fails