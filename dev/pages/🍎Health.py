import streamlit as st
import pandas as pd
import datetime
from utils.database import init_db, encrypt_data, decrypt_data
from utils.integrations import load_apple_health_data
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use the key from .env
key = os.getenv('FERNET_KEY').encode()

# Initialize DB
conn = init_db()
c = conn.cursor()

# Page Title
st.title("🏥 Health Tracker")

# Sidebar for Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose an action", ["Log Data", "View Trends", "Import Apple Health Data"])

# Log Data Form
if option == "Log Data":
    st.header("Log Your Health Data")
    date = st.date_input("Date", datetime.date.today())
    sleep = st.number_input("Sleep (hours)", min_value=0.0, max_value=24.0, step=0.5)
    mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry", "😴 Tired"])
    water = st.number_input("Water Intake (glasses)", min_value=0, max_value=20, step=1)
    food = st.text_area("Food & Beverages (e.g., 1 apple, 2 glasses of brew coffee)")

    if st.button("Submit"):
        # Encrypt mood before saving
        encrypted_mood = encrypt_data(mood, key)
        c.execute("INSERT INTO health_data (date, sleep, water, mood, food_beverages) VALUES (?, ?, ?, ?, ?)",
                  (date, sleep, water, encrypted_mood, food))
        conn.commit()
        st.success("Data logged successfully!")

# View Trends
elif option == "View Trends":
    st.header("Health Trends")
    health_data = pd.read_sql("SELECT * FROM health_data", conn)
    health_data['mood'] = health_data['mood'].apply(lambda x: decrypt_data(x, key))  # Decrypt mood

    # Sleep Trends
    st.subheader("Sleep Trends")
    st.line_chart(health_data.set_index('date')['sleep'])

    # Mood Distribution
    st.subheader("Mood Distribution")
    st.bar_chart(health_data['mood'].value_counts())

    # Correlation: Mood vs. Sleep
    st.subheader("Mood vs. Sleep")
    mood_sleep = health_data[['mood', 'sleep']]
    st.scatter_chart(mood_sleep, x='sleep', y='mood')

# Import Apple Health Data
elif option == "Import Apple Health Data":
    st.header("Import Apple Health Data")
    uploaded_file = st.file_uploader("Upload Apple Health Export (XML)", type="xml")
    if uploaded_file is not None:
        load_apple_health_data(uploaded_file)