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
def health_db():
    conn = sqlite3.connect('health.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS health_data (
                    id INTEGER PRIMARY KEY,
                    date DATE,
                    sleep REAL,
                    mood TEXT,
                    water INTEGER,
                    food_beverages TEXT,
                    calories REAL,
                    protein REAL,
                    carbs REAL,
                    fats REAL
                )''')
    conn.commit()
    return conn

def finance_db():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions_data (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    type TEXT,
                    category TEXT,
                    amount REAL,
                    description TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY,
                    category TEXT,
                    budget REAL,
                    month TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS assets (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    type TEXT,
                    amount REAL,
                    description TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS liabilities (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    type TEXT,
                    amount REAL,
                    description TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS goals (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    target_amount REAL,
                    current_amount REAL,
                    deadline TEXT
                )''')
    conn.commit()
    return conn

def projects_db():
    conn = sqlite3.connect('projects.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    status TEXT,
                    start_date TEXT,
                    deadline TEXT,
                    progress REAL DEFAULT 0.0,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    name TEXT,
                    completed INTEGER DEFAULT 0,
                    deadline TEXT,
                    notes TEXT,
                    FOREIGN KEY (project_id) REFERENCES projects (id)
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS time_logs (
                    id INTEGER PRIMARY KEY,
                    task_id INTEGER,
                    date TEXT,
                    hours REAL,
                    notes TEXT,
                    FOREIGN KEY (task_id) REFERENCES tasks (id)
                )''')
    conn.commit()
    return conn

def personal_development_db():
    conn = sqlite3.connect('personal_development.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS skills (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    start_date TEXT,
                    target_date TEXT,
                    progress REAL,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    start_date TEXT,
                    target_date TEXT,
                    progress REAL,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS courses (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    platform TEXT,
                    start_date TEXT,
                    target_date TEXT,
                    progress REAL,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS personal_goals (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    target_date TEXT,
                    progress REAL,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS journal_entries (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    entry TEXT,
                    notes TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS networking_activities (
                    id INTEGER PRIMARY KEY,
                    event_name TEXT,
                    date TEXT,
                    notes TEXT
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