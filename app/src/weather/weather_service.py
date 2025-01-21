import streamlit as st
import requests
from datetime import datetime
import json
import os
from PIL import Image
import openai
from src.wardrobe.clothing_manager import load_user_clothing

def get_weather(city):
    """Get weather data for a given city"""
    api_key = os.getenv("WEATHER_API_KEY")
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        response = requests.get(f"{base_url}?q={city}&appid={api_key}&units=metric")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error fetching weather data: {str(e)}")
        return None

def suggest_weather_appropriate_outfit(weather_data, wardrobe_items):
    """Get GPT-4 suggestions for weather-appropriate outfits"""
    if not weather_data:
        return None
        
    temp = weather_data['main']['temp']
    weather_desc = weather_data['weather'][0]['description']
    
    prompt = f"""Given the current weather conditions:
    Temperature: {temp}°C
    Weather: {weather_desc}
    
    And these available clothing items:
    {wardrobe_items[['name', 'type_of_clothing', 'color', 'season']].to_string()}
    
    Suggest an appropriate outfit using only the available items listed above.
    Return ONLY the exact names of the clothing items, one per line."""
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fashion expert specializing in weather-appropriate outfit suggestions."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip().split('\n')
    except Exception as e:
        st.error(f"Error getting outfit suggestions: {str(e)}")
        return None

def display_weather_outfit_recommendations():
    """Display weather-based outfit recommendations"""
    st.title("🌤️ Weather-Based Outfit Suggestions")
    
    # City input
    city = st.text_input("Enter your city:", placeholder="e.g., London")
    
    if city:
        # Get weather data
        weather_data = get_weather(city)
        
        if weather_data:
            # Display current weather
            temp = weather_data['main']['temp']
            weather_desc = weather_data['weather'][0]['description']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Temperature", f"{temp}°C")
            with col2:
                st.metric("Weather", weather_desc.capitalize())
            
            # Get user's wardrobe
            wardrobe = load_user_clothing()
            
            if wardrobe.empty:
                st.warning("Please add some clothes to your wardrobe first!")
                return
            
            # Get outfit suggestions
            suggested_items = suggest_weather_appropriate_outfit(weather_data, wardrobe)
            
            if suggested_items:
                st.markdown("### 👔 Suggested Outfit")
                
                cols = st.columns(3)
                for idx, item_name in enumerate(suggested_items):
                    item_name = item_name.strip()
                    matching_item = wardrobe[wardrobe['name'].str.lower() == item_name.lower()]
                    
                    if not matching_item.empty:
                        with cols[idx % 3]:
                            try:
                                image_path = matching_item.iloc[0]['image_path']
                                if os.path.exists(image_path):
                                    image = Image.open(image_path)
                                    st.image(image, caption=item_name, use_column_width=True)
                                else:
                                    st.warning(f"Image not found for: {item_name}")
                            except Exception as e:
                                st.error(f"Error displaying image for: {item_name}")
                
                # Option to save outfit
                if st.button("💾 Save this outfit"):
                    st.session_state['temp_outfit'] = {
                        'items': suggested_items,
                        'weather': {
                            'temperature': temp,
                            'description': weather_desc,
                            'date': datetime.now().strftime("%Y-%m-%d")
                        }
                    }
                    st.success("Outfit saved! You can view it in your Saved Outfits.")

def weather_based_outfits():
    """Main function for weather-based outfit recommendations"""
    display_weather_outfit_recommendations() 