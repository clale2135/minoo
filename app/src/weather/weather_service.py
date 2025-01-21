import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import os

def get_weather(city):
    """Get weather data for a city using OpenWeatherMap API"""
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        st.error("OpenWeather API key not found. Please set the OPENWEATHER_API_KEY environment variable.")
        return None

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

def suggest_weather_appropriate_outfit(weather_data, user_clothing, style_aesthetic):
    """Suggest an outfit based on weather conditions"""
    if not weather_data:
        return None

    temp = weather_data["main"]["temp"]
    weather_desc = weather_data["weather"][0]["main"].lower()
    
    # Filter clothing based on weather conditions
    suitable_items = []
    
    # Temperature-based filtering
    if temp < 10:  # Cold
        suitable_items.extend(user_clothing[user_clothing["season"].str.contains("Winter", case=False)])
    elif temp < 20:  # Mild
        suitable_items.extend(user_clothing[user_clothing["season"].str.contains("Spring|Fall", case=False)])
    else:  # Warm
        suitable_items.extend(user_clothing[user_clothing["season"].str.contains("Summer", case=False)])
    
    # Weather condition-based filtering
    if "rain" in weather_desc or "drizzle" in weather_desc:
        # Prefer water-resistant items
        suitable_items = [item for item in suitable_items if "waterproof" in str(item.get("additional_details", "")).lower()]
    
    # Style aesthetic filtering
    if style_aesthetic:
        suitable_items = [item for item in suitable_items if style_aesthetic.lower() in str(item.get("additional_details", "")).lower()]
    
    return suitable_items if suitable_items else None

def weather_based_outfits():
    """Display weather-based outfit suggestions"""
    st.title("Weather-Based Outfit Suggestions")
    
    city = st.text_input("Enter your city:")
    if city:
        weather_data = get_weather(city)
        if weather_data:
            st.write(f"Current temperature: {weather_data['main']['temp']}°C")
            st.write(f"Weather conditions: {weather_data['weather'][0]['description']}")
            
            # Get user's clothing data
            user_clothing = pd.read_csv(f"{st.session_state.username}_clothing.csv")
            style_aesthetic = st.session_state.get("style_aesthetic", None)
            
            # Get outfit suggestions
            suggested_items = suggest_weather_appropriate_outfit(weather_data, user_clothing, style_aesthetic)
            
            if suggested_items:
                st.subheader("Suggested Outfits")
                # Display suggested outfits
                for item in suggested_items:
                    st.write(f"- {item['name']} ({item['type_of_clothing']})")
            else:
                st.info("No suitable outfits found for current weather conditions.") 