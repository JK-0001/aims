import streamlit as st
import pandas as pd
import plotly.express as px
import calmap
import matplotlib.pyplot as plt
import datetime
from utils.database import health_db, encrypt_data, decrypt_data
from utils.integrations import load_apple_health_data
from utils.nutrition import get_nutrition_data
from utils.ai import predict_mood
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use the key from .env
key = os.getenv('FERNET_KEY').encode()

# Initialize DB
conn = health_db()
c = conn.cursor()

# Page Title
st.title("🍎 Health Tracker")

# Sidebar for Navigation
st.sidebar.header("Navigation")
option = st.sidebar.radio("Choose an action", ["Log Data", "View Trends", "Import Apple Health Data", "AI Insights"])

# Log Data Form
if option == "Log Data":
    st.header("Log Your Health Data")
    date = st.date_input("Date", datetime.date.today())
    sleep = st.number_input("Sleep (hours)", min_value=0.0, max_value=24.0, step=0.5)
    mood = st.selectbox("Mood", ["😊 Happy", "😐 Neutral", "😢 Sad", "😡 Angry", "😴 Tired"])
    water = st.number_input("Water Intake (glasses)", min_value=0, max_value=20, step=1)
    food = st.text_area("Food & Beverages (e.g., 1 apple, 2 glasses of brew coffee)")

    if st.button("Submit"):
        # Fetch nutrition data
        nutrition = get_nutrition_data(food) if food else None

        # Encrypt mood before saving
        encrypted_mood = encrypt_data(mood, key)
        c.execute("""INSERT INTO health_data 
                    (date, sleep, water, mood, food_beverages, calories, protein, carbs, fats) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (date, sleep, water, encrypted_mood, food,
                   nutrition['calories'] if nutrition else None,
                   nutrition['protein'] if nutrition else None,
                   nutrition['carbs'] if nutrition else None,
                   nutrition['fats'] if nutrition else None))
        conn.commit()
        st.success("Data logged successfully!")

# View Trends
elif option == "View Trends":
    st.header("Health Trends")
    health_data = pd.read_sql("SELECT * FROM health_data", conn)
    health_data['mood'] = health_data['mood'].apply(lambda x: decrypt_data(x, key))  # Decrypt mood

    # Sleep Trends
    st.subheader("Sleep Trends")
    # st.line_chart(health_data.set_index('date')['sleep'])
    fig = px.line(health_data, x='date', y='sleep', title="Sleep Over Time")
    st.plotly_chart(fig)

    # Mood Distribution
    st.subheader("Mood Distribution")
    # st.bar_chart(health_data['mood'].value_counts())
    mood_counts = health_data['mood'].value_counts().reset_index()
    mood_counts.columns = ['Mood', 'Count']
    fig = px.bar(mood_counts, x='Mood', y='Count', title="Mood Distribution")
    st.plotly_chart(fig)

    # Correlation: Mood vs. Sleep
    st.subheader("Mood vs. Sleep")
    mood_sleep = health_data[['mood', 'sleep']]
    st.scatter_chart(mood_sleep, x='sleep', y='mood')

    # Nutrition Trends
    st.subheader("Nutrition Trends")
    if 'calories' in health_data.columns:
        st.line_chart(health_data.set_index('date')['calories'])
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Avg Protein (g)", health_data['protein'].mean().round(1))
        with col2:
            st.metric("Avg Carbs (g)", health_data['carbs'].mean().round(1))
        with col3:
            st.metric("Avg Fats (g)", health_data['fats'].mean().round(1))

    # Water Intake Heatmap
    st.subheader("Water Intake Heatmap")
    health_data['date'] = pd.to_datetime(health_data['date'])
    health_data.set_index('date', inplace=True)
    fig, ax = calmap.calendarplot(health_data['water'], fig_kws={'figsize': (10, 4)})
    st.pyplot(fig)

# Import Apple Health Data
elif option == "Import Apple Health Data":
    st.header("Import Apple Health Data")
    uploaded_file = st.file_uploader("Upload Apple Health Export (XML)", type="xml")
    if uploaded_file is not None:
        load_apple_health_data(uploaded_file)

# AI Insights
elif option == "AI Insights":
    st.header("AI Insights")
    health_data = pd.read_sql("SELECT * FROM health_data", conn)
    health_data['mood'] = health_data['mood'].apply(lambda x: decrypt_data(x, key))  # Decrypt mood

    if not health_data.empty:
        # Predict Mood
        st.subheader("Mood Prediction")
        predicted_mood = predict_mood(health_data)
        st.write(f"Based on your recent data, your predicted mood is: **{predicted_mood}**")

        # Provide Suggestions
        st.subheader("Suggestions")
        avg_protein = health_data['protein'].mean()
        if avg_protein < 50:  # Example threshold
            st.error("⚠️ Your protein intake is low. Consider adding more protein-rich foods like chicken, eggs, or beans.")
        else:
            st.success("✅ Your protein intake is on track!")

        avg_sleep = health_data['sleep'].mean()
        if avg_sleep < 7:
            st.error("⚠️ You're not getting enough sleep. Aim for 7-9 hours per night.")
        else:
            st.success("✅ Your sleep is on track!")

        avg_water = health_data['water'].mean()
        if avg_water < 8:
            st.error("⚠️ You're not drinking enough water. Aim for 8 glasses per day.")
        else:
            st.success("✅ Your water intake is on track!")
    else:
        st.warning("Not enough data to generate insights. Please log more health data.")