import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load API keys from .env
load_dotenv()
APP_ID = os.getenv('APP_ID')
API_KEY = os.getenv('API_KEY')

def get_nutrition_data(query):
    """
    Fetch nutrition data for a food/drink query using Nutritionix API.
    Returns: calories, protein, carbs, fats.
    """
    endpoint = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": APP_ID,
        "x-app-key": API_KEY,
        "Content-Type": "application/json"
    }
    data = {"query": query}

    try:
        response = requests.post(endpoint, headers=headers, json=data)
        response.raise_for_status()
        food_data = response.json()['foods'][0]  # Take the first result
        return {
            "calories": food_data['nf_calories'],
            "protein": food_data['nf_protein'],
            "carbs": food_data['nf_total_carbohydrate'],
            "fats": food_data['nf_total_fat']
        }
    except Exception as e:
        st.error(f"Nutrition API error: {e}")
        return None