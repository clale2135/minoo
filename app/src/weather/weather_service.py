import streamlit as st
import requests
import os
from datetime import datetime
from ..wardrobe.clothing_manager import load_user_clothing
from ..utils.gpt_helpers import suggest_weather_appropriate_outfit

def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")
    # ... rest of the function code ...

def weather_based_outfits():
    st.title("🌤️ Weather-Based Outfit Suggestions")
    # ... rest of the function code ... 