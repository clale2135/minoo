import streamlit as st
import pandas as pd
<<<<<<< HEAD
import json
import os
from datetime import datetime, timedelta
import uuid
from PIL import Image
import time
import re
import numpy as np
import io
from openai import OpenAI
from pydantic import BaseModel
import hashlib
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv
try:
    import pyperclip
except ImportError:
    # Fallback if pyperclip is not available
    class PyperclipFallback:
        def copy(self, text):
            st.code(text, language=None)
    pyperclip = PyperclipFallback()

from src.styles.color_analysis import analyze_colors_with_imagga, determine_color_season, get_season_colors
from src.utils.gpt_helpers import gpt4_structured_response
from src.wardrobe.clothing_manager import load_user_clothing, save_user_clothing, check_duplicate_name, suggest_unique_name

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
serpapi_key = os.getenv("SERPAPI_API_KEY")
client = OpenAI(api_key=api_key)
USER_DB_PATH = "user_db.csv"

class ClothingItemResponse:
    def __init__(self, name: str, color: str, type_of_clothing: str, season: str, occasion: str, additional_details: str = ""):
        self.name = name
        self.color = color
        self.type_of_clothing = type_of_clothing
        self.season = season
        self.occasion = occasion
        self.additional_details = additional_details

def set_custom_style():
   st.markdown("""
       <style>
       /* Luxury color scheme */
       :root {
           --primary-color: #B8860B;      /* Dark Golden */
           --primary-hover: #DAA520;      /* Golden */
           --background: #FDFBF7;         /* Cream White */
           --text-color: #000000;         /* Pure Black */
           --border-color: #D4C4B7;       /* Warm Gray */
           --accent-color: #4A4039;       /* Rich Brown */
           --gold-gradient: linear-gradient(135deg, #B8860B 0%, #DAA520 100%);
       }


       /* Main container styling */
       .stApp {
           background-color: var(--background);
           background-image:
               linear-gradient(rgba(253, 251, 247, 0.97), rgba(253, 251, 247, 0.97)),
               url('https://subtle-patterns.com/patterns/white-leather.png');
       }
      
       .main {
           max-width: 1400px;
           margin: 0 auto;
           padding: 3rem;
       }
      
       /* Header styling */
       .stTitle {
           color: var(--text-color);
           font-family: 'Playfair Display', Georgia, serif;
           font-weight: 600;
           padding-bottom: 2rem;
           border-bottom: 2px solid var(--border-color);
           margin-bottom: 2rem;
           letter-spacing: 0.5px;
       }
      
       /* Button styling */
       .stButton > button {
           background: var(--gold-gradient);
           color: white;
           border-radius: 4px;
           padding: 0.8rem 1.5rem;
           border: none;
           font-weight: 500;
           letter-spacing: 0.5px;
           text-transform: uppercase;
           font-size: 0.9rem;
           transition: all 0.3s ease;
           box-shadow: 0 2px 4px rgba(184, 134, 11, 0.1);
       }
      
       .stButton > button:hover {
           transform: translateY(-2px);
           box-shadow: 0 4px 12px rgba(184, 134, 11, 0.2);
           background: var(--primary-hover);
       }
      
       /* Sidebar styling with black background */
       .css-1d391kg, [data-testid="stSidebar"] {
           background-color: #000000 !important;
           border-right: 1px solid var(--border-color);
           box-shadow: 2px 0 20px rgba(0, 0, 0, 0.05);
       }
      
       /* Sidebar text color including dropdown */
       [data-testid="stSidebar"] .stMarkdown,
       [data-testid="stSidebar"] .stSelectbox,
       [data-testid="stSidebar"] label,
       [data-testid="stSidebar"] div,
       [data-testid="stSidebar"] p,
       [data-testid="stSidebar"] span,
       [data-testid="stSidebar"] .stSelectbox > div,
       [data-testid="stSidebar"] select,
       [data-testid="stSidebar"] option {
           color: white !important;
       }


       /* Dropdown specific styling */
       [data-testid="stSidebar"] .stSelectbox > div > div {
           background-color: transparent !important;
           color: white !important;
       }


       [data-testid="stSidebar"] .stSelectbox > div > div > div {
           background-color: transparent !important;
           color: white !important;
       }


       /* Dropdown arrow color */
       [data-testid="stSidebar"] .stSelectbox svg {
           color: white !important;
       }


       /* Dropdown options when expanded */
       [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] > div {
           background-color: black !important;
           color: white !important;
       }


       [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] ul {
           background-color: black !important;
       }


       [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] li {
           color: white !important;
       }


       /* Hover state for dropdown options */
       [data-testid="stSidebar"] .stSelectbox [data-baseweb="select"] li:hover {
           background-color: rgba(255, 255, 255, 0.1) !important;
       }


       /* Sidebar button styling */
       [data-testid="stSidebar"] .stButton > button {
           background: rgba(255, 255, 255, 0.1);
           border: 1px solid rgba(255, 255, 255, 0.2);
           color: white !important;
       }


       [data-testid="stSidebar"] .stButton > button:hover {
           background: rgba(255, 255, 255, 0.2);
       }


       /* Ensure all text elements in sidebar are white */
       [data-testid="stSidebar"] * {
           color: white !important;
       }


       /* Card-like containers for clothes */
       .clothes-card {
           background-color: white;
           border-radius: 8px;
           padding: 2rem;
           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
           margin-bottom: 2rem;
           border: 1px solid rgba(212, 196, 183, 0.3);
           transition: all 0.3s ease;
       }
      
       .clothes-card:hover {
           transform: translateY(-3px);
           box-shadow: 0 8px 30px rgba(0, 0, 0, 0.1);
       }
      
       /* Image styling */
       .stImage {
           border-radius: 8px;
           overflow: hidden;
           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
       }
      
       /* Input field styling */
       .stTextInput > div > div > input {
           border-radius: 4px;
           border: 1px solid var(--border-color);
           padding: 0.8rem 1rem;
           background-color: rgba(255, 255, 255, 0.8);
           transition: all 0.2s ease;
       }
      
       .stTextInput > div > div > input:focus {
           border-color: var(--primary-color);
           box-shadow: 0 0 0 2px rgba(184, 134, 11, 0.1);
           background-color: white;
       }
      
       /* Multiselect styling */
       .stMultiSelect > div > div > div {
           border-radius: 4px;
           border: 1px solid var(--border-color);
           background-color: rgba(255, 255, 255, 0.8);
       }
      
       /* Success message styling */
       .stSuccess {
           background-color: #E8F3E8;
           color: #000000;
           padding: 1rem;
           border-radius: 4px;
           border-left: 4px solid #285E28;
           margin: 1rem 0;
       }
      
       /* Error message styling */
       .stError {
           background-color: #FBE9E7;
           color: #000000;
           padding: 1rem;
           border-radius: 4px;
           border-left: 4px solid #C62828;
           margin: 1rem 0;
       }


       /* Remove default backgrounds */
       .element-container {
           background-color: transparent !important;
       }
      
       .stDataFrame {
           background-color: transparent !important;
       }


       /* Welcome message styling */
       .welcome-msg {
           color: var(--text-color);
           text-align: center;
           padding: 3rem 0;
           margin-bottom: 3rem;
           font-size: 1.3rem;
           line-height: 1.8;
           font-family: 'Playfair Display', Georgia, serif;
           border-bottom: 1px solid var(--border-color);
       }


       /* Container styling */
       .st-emotion-cache-1y4p8pa {
           max-width: 1400px;
           padding: 3rem;
       }


       /* Form element spacing */
       .stSelectbox, .stMultiSelect {
           margin-bottom: 1.5rem;
       }


       /* Custom heading styles */
       h1, h2, h3 {
           font-family: 'Playfair Display', Georgia, serif;
           color: var(--text-color);
           letter-spacing: 0.5px;
       }


       /* Selectbox styling */
       .stSelectbox > div > div > div {
           background-color: white;
           border: 1px solid var(--border-color);
           border-radius: 4px;
           padding: 0.5rem;
       }


       /* Table styling */
       .dataframe {
           border: 1px solid var(--border-color);
           border-radius: 8px;
           overflow: hidden;
           background: white;
           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
       }


       .dataframe th {
           background-color: #F8F5F1;
           color: var(--text-color);
           font-weight: 600;
           padding: 1rem;
           border-bottom: 2px solid var(--border-color);
       }


       .dataframe td {
           padding: 0.8rem 1rem;
           border-bottom: 1px solid var(--border-color);
       }


       /* Add decorative elements */
       .stTitle::before {
           content: "✦";
           color: var(--primary-color);
           margin-right: 1rem;
           font-size: 1.2em;
       }


       .stTitle::after {
           content: "✦";
           color: var(--primary-color);
           margin-left: 1rem;
           font-size: 1.2em;
       }


       /* Sidebar header */
       .sidebar .sidebar-content {
           background-color: #FFFFFF;
           padding: 2rem 1rem;
       }


       /* Toast styling */
       .stToast {
           background-color: white !important;
           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1) !important;
           border: 1px solid var(--border-color) !important;
           border-radius: 8px !important;
           padding: 1rem !important;
       }


       /* Update text colors in specific elements */
       .stTitle, h1, h2, h3, p, .welcome-msg, .stTextInput > div > div > input {
           color: #000000 !important;
       }


       /* Table text color */
       .dataframe th, .dataframe td {
           color: #000000 !important;
       }


       /* Success and error messages remain colored for visibility */
       .stSuccess {
           background-color: #E8F3E8;
           color: #000000;
           padding: 1rem;
           border-radius: 4px;
           border-left: 4px solid #285E28;
           margin: 1rem 0;
       }
      
       .stError {
           background-color: #FBE9E7;
           color: #000000;
           padding: 1rem;
           border-radius: 4px;
           border-left: 4px solid #C62828;
           margin: 1rem 0;
       }


       /* Ensure all regular text is black */
       div, span, label, .stMarkdown {
           color: #000000 !important;
       }


       /* Keep button text white for contrast */
       .stButton > button {
           color: white !important;
       }


       /* Comprehensive sidebar and dropdown styling */
       [data-testid="stSidebar"] {
           background-color: #000000;
       }


       /* Target all text elements in sidebar */
       [data-testid="stSidebar"] * {
           color: white !important;
       }


       /* Specific dropdown styling */
       [data-testid="stSidebar"] [data-baseweb="select"] {
           color: white !important;
       }


       [data-testid="stSidebar"] [data-baseweb="select"] * {
           color: white !important;
           background-color: black !important;
       }


       /* Dropdown menu items */
       [data-baseweb="popover"] * {
           color: white !important;
           background-color: black !important;
       }


       [data-baseweb="select"] [role="listbox"] {
           background-color: black !important;
       }


       [data-baseweb="select"] [role="option"] {
           color: white !important;
           background-color: black !important;
       }


       /* Hover state for dropdown options */
       [data-baseweb="select"] [role="option"]:hover {
           background-color: #333333 !important;
       }


       /* Selected option in dropdown */
       [data-baseweb="tag"] {
           background-color: #333333 !important;
           color: white !important;
       }


       /* Multiselect tag styling for both sidebar and main content */
       [data-baseweb="tag"] {
           background-color: #333333 !important;
           border: 1px solid rgba(255, 255, 255, 0.2) !important;
       }


       [data-baseweb="tag"] span {
           color: white !important;
       }


       /* Close button (x) in the tag */
       [data-baseweb="tag"] button {
           color: white !important;
       }


       /* Hover state for the close button */
       [data-baseweb="tag"] button:hover {
           background-color: rgba(255, 255, 255, 0.1) !important;
       }


       /* Make sure the text inside multiselect is visible */
       .stMultiSelect div[role="button"] span {
           color: black !important;
       }


       /* Selected tags in multiselect */
       .stMultiSelect [data-baseweb="tag"] {
           background-color: #333333 !important;
       }


       .stMultiSelect [data-baseweb="tag"] span {
           color: white !important;
       }


       /* Dropdown items */
       .stMultiSelect [role="listbox"] div {
           color: black !important;
       }


       </style>
   """, unsafe_allow_html=True)




set_custom_style()




# Utility functions for user management
def hash_password(password):
   return hashlib.sha256(password.encode()).hexdigest()




def load_user_db():
   if not os.path.exists(USER_DB_PATH):
       df = pd.DataFrame(columns=["username", "password"])
       df.to_csv(USER_DB_PATH, index=False)
   try:
       df = pd.read_csv(USER_DB_PATH)
   except pd.errors.EmptyDataError:
       df = pd.DataFrame(columns=["username", "password"])
   return df




def save_user_db(df):
   df.to_csv(USER_DB_PATH, index=False)




def user_exists(username):
   df = load_user_db()
   return username in df["username"].values




def add_user(username, password):
   df = load_user_db()
   hashed_password = hash_password(password)
   new_user = pd.DataFrame({"username": [username], "password": [hashed_password]})
   df = pd.concat([df, new_user], ignore_index=True)
   save_user_db(df)




def verify_user(username, password):
   df = load_user_db()
   hashed_password = hash_password(password)
   if username in df["username"].values:
       stored_password = df[df["username"] == username]["password"].values[0]
       return stored_password == hashed_password
   return False




# User authentication functions
def create_account():
   st.title("Create Account")
   username = st.text_input("Enter a username")
   password = st.text_input("Enter a password", type="password")

   if st.button("Create Account"):
       if user_exists(username):
           st.error("Username already exists.")
       else:
           add_user(username, password)
           st.success("Account created successfully!")
           
           # Set session state for new user
           st.session_state.logged_in = True
           st.session_state.username = username
           st.session_state.show_style_quiz = True  # New flag to show quiz
           st.rerun()




def login():
   if "logged_in" in st.session_state and st.session_state.logged_in:
       st.title(f"Welcome back, {st.session_state.username}!")
       return


   st.title("Login")
   username = st.text_input("Username")
   password = st.text_input("Password", type="password")


   if st.button("Login"):
       if verify_user(username, password):
           st.session_state.logged_in = True
           st.session_state.username = username
           st.toast("Login successful!", icon="✅")
           st.rerun()
       else:
           st.toast("Invalid username or password.", icon="❌")




# GPT-4 Structured Clothing Response
@st.cache_data
def gpt4o_structured_clothing(item_description: str):
   prompt = """You are an expert in fashion. Please provide a brief, descriptive name for this clothing item.
   Return your response in this exact format:
   {
       "name": "Brief descriptive name (2-4 words)",
       "color": "Primary color",
       "type_of_clothing": "Category",
       "season": "Primary season",
       "occasion": "Primary occasion",
       "additional_details": ""
   }
  
   Focus on creating a concise, professional name that would appear in a luxury store catalog.
   Examples:
   - "Classic White Oxford Shirt"
   - "Navy Wool Peacoat"
   - "Silk Evening Gown"
   - "Tailored Charcoal Trousers"
  
   Keep the name brief but descriptive, highlighting key features like material, style, or cut."""

   try:
       response = client.chat.completions.create(
           model="gpt-4",
           messages=[
               {"role": "system", "content": prompt},
               {"role": "user", "content": item_description}
           ]
       )
      
       response_text = response.choices[0].message.content.strip()
       clothing_data = json.loads(response_text)
      
       return ClothingItemResponse(
           name=clothing_data.get('name', ''),
           color=clothing_data.get('color', ''),
           type_of_clothing=clothing_data.get('type_of_clothing', ''),
           season=clothing_data.get('season', ''),
           occasion=clothing_data.get('occasion', ''),
           additional_details=clothing_data.get('additional_details', '')
       )
   except Exception as e:
       return ClothingItemResponse(
           name="New Item",
           color="",
           type_of_clothing="",
           season="All Seasons",
           occasion="Casual",
           additional_details=""
       )

def fetch_product_images(search_query):
    """Fetch product images and details from Google Shopping"""
    try:
        params = {
            "engine": "google_shopping",
            "q": search_query,
            "api_key": serpapi_key,
            "num": 5  # Limit to 5 results
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        if "shopping_results" in results:
            products = []
            for item in results["shopping_results"][:5]:
                products.append({
                    "title": item.get("title", ""),
                    "price": item.get("price", ""),
                    "link": item.get("link", ""),
                    "image": item.get("thumbnail", ""),
                    "source": item.get("source", "")
                })
            return products
        return []
    except Exception as e:
        st.error(f"Error fetching products: {str(e)}")
        return []

def suggest_internet_clothes():
    """Suggest clothes from the internet that would complement the user's wardrobe"""
    st.title("🔍 AI Shopping Assistant")
    
    # Load user's existing wardrobe
    user_clothing = load_user_clothing()
    
    if user_clothing.empty:
        st.info("Add some clothes to your wardrobe first so we can suggest complementary pieces!")
        return
    
    # Analyze current wardrobe
    wardrobe_analysis = f"""Current wardrobe summary:
    - Types: {', '.join(user_clothing['type_of_clothing'].unique())}
    - Colors: {', '.join(user_clothing['color'].unique())}
    - Occasions: {', '.join(user_clothing['occasion'].str.split(',').explode().unique())}
    - Seasons: {', '.join(user_clothing['season'].str.split(',').explode().unique())}
    """
    
    # Options for what kind of suggestions user wants
    st.markdown("### 🛍️ Find New Clothes")
    search_type = st.radio(
        "What would you like to find?",
        ["Fill Wardrobe Gaps", "Complete Specific Outfit", "Find Similar to Existing Item"]
    )
    
    if search_type == "Fill Wardrobe Gaps":
        prompt = f"""Based on this wardrobe:
        {wardrobe_analysis}
        
        Identify 3 specific clothing items that would fill gaps in the wardrobe and enhance its versatility.
        Consider the existing colors, styles, and occasions.
        
        For each item, provide:
        1. Specific description (e.g., "Navy blue wool blazer with gold buttons")
        2. Why it would enhance the wardrobe
        3. What it would pair well with
        4. Suggested price range
        5. Keywords to search for online
        6. Google Shopping search query
        
        Return in JSON format:
        {{
            "suggestions": [
                {{
                    "description": "item description",
                    "reasoning": "why it would help",
                    "pairings": ["existing items"],
                    "price_range": "range in USD",
                    "search_keywords": ["keyword1", "keyword2"],
                    "shopping_query": "exact query for google shopping"
                }}
            ]
        }}"""
        
    elif search_type == "Complete Specific Outfit":
        occasion = st.selectbox(
            "What's the occasion?",
            ["Casual", "Business", "Formal", "Party", "Outdoor", "Workout"]
        )
        existing_items = st.multiselect(
            "Select items you want to use in this outfit",
            user_clothing['name'].tolist()
        )
        
        prompt = f"""Create an outfit for {occasion} occasion using these existing items:
        {', '.join(existing_items)}
        
        Suggest 2-3 additional items to complete the outfit.
        
        For each suggested item provide:
        1. Specific description
        2. Why it complements the existing items
        3. Suggested price range
        4. Keywords to search for online
        5. Google Shopping search query
        
        Return in JSON format:
        {{
            "suggestions": [
                {{
                    "description": "item description",
                    "reasoning": "why it works",
                    "price_range": "range in USD",
                    "search_keywords": ["keyword1", "keyword2"],
                    "shopping_query": "exact query for google shopping"
                }}
            ]
        }}"""
        
    else:  # Find Similar to Existing Item
        reference_item = st.selectbox(
            "Select an item you'd like to find something similar to",
            user_clothing['name'].tolist()
        )
        selected_item = user_clothing[user_clothing['name'] == reference_item].iloc[0]
        
        prompt = f"""Find 3 variations of this item:
        - Name: {selected_item['name']}
        - Type: {selected_item['type_of_clothing']}
        - Color: {selected_item['color']}
        
        Suggest similar items with different:
        - Colors
        - Materials
        - Styles
        - Price points
        
        Return in JSON format:
        {{
            "suggestions": [
                {{
                    "description": "item description",
                    "variation": "how it differs",
                    "price_range": "range in USD",
                    "search_keywords": ["keyword1", "keyword2"],
                    "shopping_query": "exact query for google shopping"
                }}
            ]
        }}"""
    
    if st.button("Get AI Suggestions"):
        with st.spinner("🔍 Searching for perfect additions to your wardrobe..."):
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion expert and personal shopper."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            suggestions = json.loads(response.choices[0].message.content)
            
            for idx, suggestion in enumerate(suggestions['suggestions'], 1):
                st.markdown(f"### Suggestion {idx}")
                st.markdown(f"""
                    **Description:** {suggestion['description']}
                    
                    **Why it works:** {suggestion.get('reasoning', suggestion.get('variation', ''))}
                    
                    **Price Range:** {suggestion['price_range']}
                """)
                
                # Fetch actual products using the shopping query
                products = fetch_product_images(suggestion['shopping_query'])
                
                if products:
                    st.markdown("#### 🛍️ Available Products:")
                    
                    # Create a grid of products
                    cols = st.columns(min(len(products), 3))
                    for i, product in enumerate(products):
                        with cols[i % 3]:
                            st.image(product['image'], caption=product['title'][:50] + "...")
                            st.markdown(f"**Price:** {product['price']}")
                            st.markdown(f"**Store:** {product['source']}")
                            
                            # Add to wardrobe button
                            if st.button(f"Add to Wardrobe", key=f"add_{idx}_{i}"):
                                try:
                                    # Download and save the image
                                    response = requests.get(product['image'])
                                    image = Image.open(io.BytesIO(response.content))
                                    image_filename = f"uploads/{str(uuid.uuid4())}.jpg"
                                    image.save(image_filename)
                                    
                                    # Create new clothing item
                                    new_item = pd.DataFrame([{
                                        'name': product['title'][:50],
                                        'type_of_clothing': suggestion['search_keywords'][0],
                                        'color': suggestion['search_keywords'][1] if len(suggestion['search_keywords']) > 1 else "",
                                        'season': "All Seasons",
                                        'occasion': occasion if search_type == "Complete Specific Outfit" else "Casual",
                                        'image_path': image_filename,
                                        'additional_details': f"Added from AI Shopping Assistant - {suggestion.get('reasoning', suggestion.get('variation', ''))}"
                                    }])
                                    
                                    # Add to wardrobe
                                    updated_wardrobe = pd.concat([user_clothing, new_item], ignore_index=True)
                                    if save_user_clothing(updated_wardrobe):
                                        st.success("✨ Item added to your wardrobe!")
                                    else:
                                        st.error("Failed to add item to wardrobe.")
                                except Exception as e:
                                    st.error(f"Error adding item to wardrobe: {str(e)}")
                            
                            st.markdown(f"[View Details]({product['link']})")
                else:
                    st.info("No products found for this suggestion. Try adjusting the search terms.")
                
                if suggestion.get('pairings'):
                    st.markdown(f"**Would pair well with:** {', '.join(suggestion['pairings'])}")
                
                st.markdown("---")

def style_quiz():
    st.title("Style Quiz")
    
    if "quiz_completed" not in st.session_state:
        st.session_state.quiz_completed = False
    
    if not st.session_state.quiz_completed:
        st.markdown("### Let's discover your personal style! 👗")
        
        # Basic style preferences
        style_pref = st.multiselect(
            "What styles do you typically prefer?",
            ["Casual", "Professional", "Elegant", "Sporty", "Bohemian", "Minimalist", "Vintage", "Trendy"]
        )
        
        color_pref = st.multiselect(
            "What colors do you love wearing?",
            ["Black", "White", "Navy", "Red", "Pink", "Purple", "Green", "Blue", "Yellow", "Orange", "Brown", "Gray"]
        )
        
        occasions = st.multiselect(
            "What occasions do you usually dress for?",
            ["Work", "Casual outings", "Formal events", "Sports/Active", "Date night", "Party", "Travel"]
        )
        
        # Save preferences if quiz is submitted
        if st.button("Complete Quiz"):
            if not style_pref or not color_pref or not occasions:
                st.error("Please answer all questions to complete the quiz.")
            else:
                st.session_state.style_preferences = {
                    "style_pref": style_pref,
                    "color_pref": color_pref,
                    "occasions": occasions
                }
                st.session_state.quiz_completed = True
                st.session_state.show_style_quiz = False
                st.success("Quiz completed! Your preferences have been saved.")
                st.rerun()

def show_tutorial():
    st.title("Welcome to Your Digital Wardrobe! 👋")
    
    st.markdown("""
    ### Quick Start Guide
    
    1. **Add Your Clothes** 📸
       - Go to "Image Uploader and Display"
       - Upload photos of your clothes
       - Add details like color, type, and occasion
    
    2. **Create Outfits** 👔
       - Combine your clothes into outfits
       - Get AI-powered styling suggestions
       - Save your favorite combinations
    
    3. **Plan Your Wardrobe** 📅
       - Schedule outfits for specific dates
       - Get weather-based recommendations
       - Track your most-worn items
    
    4. **Get Style Insights** 🎯
       - Analyze your wardrobe colors
       - Get personalized style tips
       - Find complementary pieces
    """)
    
    if st.button("Got it! Let's Start"):
        st.session_state.show_tutorial = False
        st.rerun()

def migrate_images():
    """Ensure the uploads directory exists and migrate any images if needed"""
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

def homepage():
    st.title(f"Welcome back, {st.session_state.username}! 👋")
    
    # Load user's wardrobe stats
    user_clothing = load_user_clothing()
    
    if not user_clothing.empty:
        # Display wardrobe statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Items", len(user_clothing))
        
        with col2:
            most_common_type = user_clothing['type_of_clothing'].mode().iloc[0] if not user_clothing.empty else "N/A"
            st.metric("Most Common Type", most_common_type)
        
        with col3:
            most_common_color = user_clothing['color'].mode().iloc[0] if not user_clothing.empty else "N/A"
            st.metric("Most Common Color", most_common_color)
        
        # Quick actions
        st.markdown("### Quick Actions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("➕ Add New Clothes"):
                st.query_params["page"] = "Image Uploader and Display"
                st.rerun()
        
        with col2:
            if st.button("👔 Create Outfit"):
                st.query_params["page"] = "Saved Outfits"
                st.rerun()
    else:
        st.info("Your wardrobe is empty! Start by adding some clothes.")
        if st.button("Add Your First Item"):
            st.query_params["page"] = "Image Uploader and Display"
            st.rerun()

def image_uploader_and_display():
    st.title("Add Clothes to Your Wardrobe 📸")
    
    uploaded_file = st.file_uploader("Choose an image", type=['png', 'jpg', 'jpeg', 'webp'])
    
    if uploaded_file is not None:
        # Create a unique filename
        file_extension = uploaded_file.name.split('.')[-1]
        unique_filename = f"uploads/{str(uuid.uuid4())}.{file_extension}"
        
        # Save the uploaded file
        with open(unique_filename, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Display the uploaded image
        st.image(unique_filename, caption="Uploaded Image", use_column_width=True)
        
        # Get clothing details
        with st.form("clothing_details"):
            st.markdown("### Item Details")
            
            # Get item description from user
            item_description = st.text_area(
                "Describe this item (color, type, style, etc.)",
                help="Example: A navy blue cotton button-down shirt with long sleeves"
            )
            
            # Use GPT-4 to structure the response if description is provided
            if item_description:
                clothing_data = gpt4o_structured_clothing(item_description)
            else:
                clothing_data = ClothingItemResponse(
                    name="New Item",
                    color="",
                    type_of_clothing="",
                    season="All Seasons",
                    occasion="Casual",
                    additional_details=""
                )
            
            # Allow user to edit the structured data
            name = st.text_input("Name", value=clothing_data.name)
            color = st.text_input("Color", value=clothing_data.color)
            type_of_clothing = st.text_input("Type", value=clothing_data.type_of_clothing)
            season = st.multiselect(
                "Season",
                ["Spring", "Summer", "Fall", "Winter"],
                default=clothing_data.season.split(",") if clothing_data.season else []
            )
            occasion = st.multiselect(
                "Occasion",
                ["Casual", "Business", "Formal", "Party", "Sport", "Beach"],
                default=clothing_data.occasion.split(",") if clothing_data.occasion else []
            )
            
            if st.form_submit_button("Save to Wardrobe"):
                # Create new clothing item
                new_item = pd.DataFrame([{
                    'name': name,
                    'type_of_clothing': type_of_clothing,
                    'color': color,
                    'season': ",".join(season),
                    'occasion': ",".join(occasion),
                    'image_path': unique_filename
                }])
                
                # Add to wardrobe
                user_clothing = load_user_clothing()
                updated_wardrobe = pd.concat([user_clothing, new_item], ignore_index=True)
                
                if save_user_clothing(updated_wardrobe):
                    st.success("✨ Item added to your wardrobe!")
                else:
                    st.error("Failed to add item to wardrobe.")

def display_saved_clothes():
    st.title("Your Wardrobe 👔")
    
    # Load user's clothes
    user_clothing = load_user_clothing()
    
    if user_clothing.empty:
        st.info("Your wardrobe is empty! Add some clothes to get started.")
        if st.button("Add Clothes"):
            st.query_params["page"] = "Image Uploader and Display"
            st.rerun()
        return
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        type_filter = st.multiselect(
            "Filter by Type",
            options=sorted(user_clothing['type_of_clothing'].unique())
        )
    
    with col2:
        color_filter = st.multiselect(
            "Filter by Color",
            options=sorted(user_clothing['color'].unique())
        )
    
    with col3:
        occasion_filter = st.multiselect(
            "Filter by Occasion",
            options=sorted(set([occ for occs in user_clothing['occasion'].str.split(',') for occ in occs]))
        )
    
    # Apply filters
    filtered_clothing = user_clothing.copy()
    if type_filter:
        filtered_clothing = filtered_clothing[filtered_clothing['type_of_clothing'].isin(type_filter)]
    if color_filter:
        filtered_clothing = filtered_clothing[filtered_clothing['color'].isin(color_filter)]
    if occasion_filter:
        filtered_clothing = filtered_clothing[filtered_clothing['occasion'].apply(lambda x: any(occ in x.split(',') for occ in occasion_filter))]
    
    # Display clothes in a grid
    cols = st.columns(3)
    for idx, (_, item) in enumerate(filtered_clothing.iterrows()):
        with cols[idx % 3]:
            if os.path.exists(item['image_path']):
                st.image(item['image_path'], use_column_width=True)
            st.markdown(f"""
                **{item['name']}**  
                Type: {item['type_of_clothing']}  
                Color: {item['color']}  
                Occasions: {item['occasion']}
            """)
            
            # Delete button
            if st.button(f"Delete {item['name']}", key=f"delete_{idx}"):
                # Remove from dataframe
                user_clothing = user_clothing.drop(user_clothing[user_clothing['name'] == item['name']].index)
                save_user_clothing(user_clothing)
                # Delete image file
                if os.path.exists(item['image_path']):
                    os.remove(item['image_path'])
                st.success(f"Deleted {item['name']}")
                st.rerun()

def clothing_data_insights():
    st.title("Wardrobe Insights 📊")
    
    # Load user's clothes
    user_clothing = load_user_clothing()
    
    if user_clothing.empty:
        st.info("Add some clothes to get insights about your wardrobe!")
        return
    
    # Basic statistics
    st.markdown("### Wardrobe Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", len(user_clothing))
    
    with col2:
        types_count = user_clothing['type_of_clothing'].value_counts()
        st.metric("Most Common Type", f"{types_count.index[0]} ({types_count.values[0]})")
    
    with col3:
        colors_count = user_clothing['color'].value_counts()
        st.metric("Most Common Color", f"{colors_count.index[0]} ({colors_count.values[0]})")
    
    # Color analysis
    st.markdown("### Color Analysis")
    colors_df = pd.DataFrame({
        'Color': colors_count.index,
        'Count': colors_count.values
    })
    st.bar_chart(colors_df.set_index('Color'))
    
    # Type distribution
    st.markdown("### Clothing Types")
    types_df = pd.DataFrame({
        'Type': types_count.index,
        'Count': types_count.values
    })
    st.bar_chart(types_df.set_index('Type'))
    
    # Get GPT-4 insights
    if st.button("Get AI Insights"):
        wardrobe_summary = f"""
        Total items: {len(user_clothing)}
        Types: {', '.join(user_clothing['type_of_clothing'].unique())}
        Colors: {', '.join(user_clothing['color'].unique())}
        Occasions: {', '.join(set([occ for occs in user_clothing['occasion'].str.split(',') for occ in occs]))}
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fashion expert analyzing a wardrobe."},
                {"role": "user", "content": f"Analyze this wardrobe and provide insights about balance, versatility, and suggestions for additions:\n{wardrobe_summary}"}
            ]
        )
        
        st.markdown("### AI Insights")
        st.markdown(response.choices[0].message.content)

<<<<<<< HEAD
def face_shape_quiz():
    """Quiz to determine user's face shape"""
    st.markdown("### 👤 Face Shape Analysis")
    st.markdown("""
        Understanding your face shape helps you choose the most flattering:
        - Hairstyles
        - Glasses frames
        - Necklines
        - Accessories
    """)
    
    questions = {
        'face_length': {
            'question': "How would you describe your face length?",
            'options': [
                "Longer than it is wide",
                "About equal in length and width",
                "Wider than it is long"
            ]
        },
        'jaw_shape': {
            'question': "Which best describes your jaw?",
            'options': [
                "Angular and sharp",
                "Rounded",
                "Square and prominent",
                "Narrow and pointed"
            ]
        },
        'cheekbones': {
            'question': "How would you describe your cheekbones?",
            'options': [
                "High and prominent",
                "Round and full",
                "Not very prominent",
                "Wide and angular"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"face_{key}"
        )
        st.markdown("---")
    
    if st.button("Determine My Face Shape", type="primary"):
        face_shape = analyze_face_shape(responses)
        show_face_shape_results(face_shape)

def body_type_quiz():
    """Quiz to determine user's body type"""
    st.markdown("### 📏 Body Type Analysis")
    st.markdown("""
        Understanding your body type helps you:
        - Choose flattering silhouettes
        - Balance your proportions
        - Create harmonious outfits
    """)
    
    questions = {
        'shoulders': {
            'question': "How would you describe your shoulders?",
            'options': [
                "Broader than my hips",
                "Same width as my hips",
                "Narrower than my hips",
                "Angular and straight"
            ]
        },
        'waist': {
            'question': "How defined is your waist?",
            'options': [
                "Very defined/curved",
                "Somewhat defined",
                "Straight with little definition",
                "Not visible/undefined"
            ]
        },
        'body_lines': {
            'question': "Which best describes your overall body lines?",
            'options': [
                "Curved and rounded",
                "Straight and angular",
                "Mixed curved and straight",
                "Soft and undefined"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"body_{key}"
        )
        st.markdown("---")
    
    if st.button("Analyze My Body Type", type="primary"):
        body_type = analyze_body_type(responses)
        show_body_type_results(body_type)

def analyze_face_shape(responses):
    """Analyze quiz responses to determine face shape"""
    prompt = f"""Based on these characteristics:
    Face length: {responses['face_length']}
    Jaw shape: {responses['jaw_shape']}
    Cheekbones: {responses['cheekbones']}
    
    Determine the person's face shape (Oval, Round, Square, Heart, Diamond, or Rectangle).
    Return ONLY the face shape name."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a face shape analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_face_shape_results(face_shape):
    """Display face shape analysis results"""
    st.success(f"Your Face Shape: {face_shape}")
    st.markdown(get_face_shape_tips(face_shape))

def get_face_shape_tips(face_shape):
    """Get styling tips for a face shape"""
    tips = {
        "Oval": "Lucky you! Most styles work well with your balanced proportions.",
        "Round": "Choose angular frames and accessories to add definition.",
        "Square": "Soften angles with curved lines and oval shapes.",
        "Heart": "Balance a wider forehead with wider bottom frames.",
        "Diamond": "Highlight your cheekbones with upswept frames.",
        "Rectangle": "Add width with round or square shapes."
    }
    return tips.get(face_shape, "No specific tips available for this face shape.")

def get_season_tips(season):
    """Get styling tips for a color season"""
    tips = {
        "Warm Spring": """
            - Wear warm, clear colors
            - Choose golden jewelry
            - Avoid dark, cool colors
            - Best neutrals are camel and warm brown
        """,
        "Cool Winter": """
            - Wear clear, cool colors
            - Choose silver jewelry
            - Avoid muted, warm colors
            - Best neutrals are navy and gray
        """,
        # Add other seasons as needed
    }
    return tips.get(season, "No specific tips available for this season.")

# Fix 1: Add missing function for analyzing body type
def analyze_body_type(responses):
    """Analyze quiz responses to determine body type"""
    prompt = f"""Based on these characteristics:
    Shoulders: {responses['shoulders']}
    Waist: {responses['waist']}
    Body lines: {responses['body_lines']}
    
    Determine the person's body type (Hourglass, Rectangle, Triangle, Inverted Triangle, or Oval).
    Return ONLY the body type name."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a body type analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Fix 2: Add missing function for showing body type results
def show_body_type_results(body_type):
    """Display body type analysis results"""
    st.success(f"Your Body Type: {body_type}")
    
    tips = {
        "Hourglass": """
            - Emphasize your natural waist
            - Choose fitted clothing that follows your curves
            - Belt dresses and tops to highlight your waist
            - Avoid boxy or oversized styles
        """,
        "Rectangle": """
            - Create curves with peplum tops and wrap dresses
            - Use belts to define your waist
            - Layer pieces to add dimension
            - Try ruffles and gathered details
        """,
        "Triangle": """
            - Draw attention upward with detailed tops
            - Choose A-line skirts and dresses
            - Opt for darker colors on bottom
            - Balance with structured shoulders
        """,
        "Inverted Triangle": """
            - Balance shoulders with fuller skirts
            - Choose V-necks and scoop necklines
            - Add volume to lower body
            - Avoid shoulder pads and puffy sleeves
        """,
        "Oval": """
            - Create vertical lines to elongate
            - Choose flowing fabrics
            - Wear empire waist styles
            - Focus on structured pieces
        """
    }
    
    st.markdown("### Styling Tips")
    st.markdown(tips.get(body_type, "No specific tips available for this body type."))

# Fix 3: Add missing function for style personality quiz
def style_personality_quiz():
    """Quiz to determine user's style personality"""
    st.markdown("### 👗 Style Personality Quiz")
    st.markdown("""
        Discover your unique style personality! This comprehensive quiz analyzes your preferences
        across multiple dimensions to help you understand and develop your personal style.
    """)
    
    questions = {
        'weekend_style': {
            'question': "What's your ideal weekend outfit?",
            'options': [
                "Comfortable athleisure (leggings, oversized sweater, sneakers)",
                "Polished casual (well-fitted jeans, blazer, loafers)",
                "Bold, artistic ensembles (mixed patterns, unique pieces)",
                "Classic, timeless basics (white shirt, tailored pants)",
                "Trendy, fashion-forward looks (latest styles, statement pieces)"
            ]
        },
        'color_approach': {
            'question': "How do you approach color in your wardrobe?",
            'options': [
                "Neutral palette with occasional pops of color",
                "Bold, vibrant colors that make a statement",
                "Soft, muted tones that blend together",
                "Monochromatic looks in varying shades",
                "Mix of bright and neutral depending on mood"
            ]
        },
        'accessories': {
            'question': "How do you approach accessories?",
            'options': [
                "Minimal and practical (simple watch, studs)",
                "Classic and coordinated (pearls, matching sets)",
                "Bold statement pieces (chunky jewelry, unique designs)",
                "Vintage or artistic pieces with history",
                "Latest trends and modern designs"
            ]
        },
        'shopping': {
            'question': "What's your shopping style?",
            'options': [
                "Quality basics that last years",
                "Investment pieces from luxury brands",
                "Unique, artistic pieces from boutiques",
                "Mix of vintage and contemporary",
                "Latest trends from fashion retailers"
            ]
        },
        'outfit_planning': {
            'question': "How do you approach outfit planning?",
            'options': [
                "Carefully coordinated the night before",
                "Capsule wardrobe with easy mixing",
                "Spontaneous based on mood",
                "Following specific style rules",
                "Inspired by current trends"
            ]
        },
        'style_icons': {
            'question': "Which style icon's aesthetic most resonates with you?",
            'options': [
                "Audrey Hepburn (timeless elegance)",
                "Kate Moss (effortless cool)",
                "Iris Apfel (bold maximalism)",
                "Steve Jobs (minimal uniformity)",
                "Rihanna (fearless experimentation)"
            ]
        },
        'comfort_vs_style': {
            'question': "How do you balance comfort and style?",
            'options': [
                "Comfort is my top priority",
                "Equal balance of both",
                "Style first, but must be wearable",
                "Willing to sacrifice comfort for look",
                "Depends on the occasion"
            ]
        },
        'pattern_preference': {
            'question': "What's your approach to patterns and prints?",
            'options': [
                "Minimal patterns, prefer solid colors",
                "Classic patterns (stripes, checks)",
                "Bold, artistic prints",
                "Mix of patterns and textures",
                "Trendy seasonal patterns"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"style_personality_{key}"
        )
        st.markdown("---")
    
    if st.button("Discover My Style Personality", type="primary"):
        personality = analyze_style_personality(responses)
        show_style_personality_results(personality)

def analyze_style_personality(responses):
    """Enhanced analysis of quiz responses to determine style personality"""
    prompt = f"""Based on these detailed style preferences:
    Weekend style: {responses['weekend_style']}
    Color approach: {responses['color_approach']}
    Accessories: {responses['accessories']}
    Shopping: {responses['shopping']}
    Outfit planning: {responses['outfit_planning']}
    Style icons: {responses['style_icons']}
    Comfort vs style: {responses['comfort_vs_style']}
    Pattern preference: {responses['pattern_preference']}
    
    Analyze these responses to determine the person's primary and secondary style personalities.
    Consider these style types:
    - Classic (timeless, polished, coordinated)
    - Romantic (feminine, soft, detailed)
    - Creative (artistic, unique, experimental)
    - Minimalist (clean, simple, modern)
    - Trendy (current, fashion-forward)
    - Dramatic (bold, statement-making)
    - Natural (comfortable, casual, effortless)
    - Elegant (sophisticated, refined, luxurious)
    
    Return the result in this format:
    Primary: [Style Type]
    Secondary: [Style Type]
    Key Characteristics: [3-4 key traits]"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert fashion psychologist specializing in personal style analysis."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_style_personality_results(personality_analysis):
    """Enhanced display of style personality results"""
    # Parse the analysis
    lines = personality_analysis.split('\n')
    primary = lines[0].split(': ')[1]
    secondary = lines[1].split(': ')[1]
    characteristics = lines[2].split(': ')[1]
    
    # Display results
    st.success("Your Style Analysis Complete!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            ### Primary Style: {primary}
            This is your dominant style preference and should guide most of your wardrobe choices.
        """)
    
    with col2:
        st.markdown(f"""
            ### Secondary Style: {secondary}
            This style influence adds depth and versatility to your primary style.
        """)
    
    st.markdown("### Key Characteristics")
    st.markdown(characteristics)
    
    # Style recommendations based on combination
    st.markdown("### Personalized Style Recommendations")
    
    recommendations = get_style_recommendations(primary, secondary)
    
    tabs = st.tabs(["Wardrobe Essentials", "Color Palette", "Styling Tips", "Shopping Guide"])
    
    with tabs[0]:
        st.markdown("#### Must-Have Pieces")
        for item in recommendations['essentials']:
            st.markdown(f"- {item}")
    
    with tabs[1]:
        st.markdown("#### Your Ideal Color Palette")
        st.markdown(recommendations['colors'])
    
    with tabs[2]:
        st.markdown("#### Styling Tips")
        for tip in recommendations['styling_tips']:
            st.markdown(f"- {tip}")
    
    with tabs[3]:
        st.markdown("#### Shopping Recommendations")
        st.markdown(recommendations['shopping_guide'])
    
    # Action steps
    st.markdown("### Next Steps")
    st.markdown("""
        1. Review your current wardrobe against these recommendations
        2. Identify gaps in your wardrobe essentials
        3. Plan your next shopping trip based on the guidelines
        4. Experiment with combining your primary and secondary styles
    """)

def get_style_recommendations(primary, secondary):
    """Get detailed style recommendations based on style combination"""
    prompt = f"""Create detailed style recommendations for someone with:
    Primary Style: {primary}
    Secondary Style: {secondary}
    
    Include:
    1. List of 10 wardrobe essentials
    2. Ideal color palette description
    3. 5 specific styling tips
    4. Shopping guide with specific store recommendations
    
    Format as a JSON with keys: essentials, colors, styling_tips, shopping_guide"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional fashion stylist creating personalized recommendations."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

def wardrobe_essentials_quiz():
    """Quiz to determine essential pieces for user's lifestyle"""
    st.markdown("### 👔 Wardrobe Essentials Quiz")
    st.markdown("""
        Let's identify the key pieces you need based on your lifestyle and preferences.
        This will help you build a functional and versatile wardrobe.
    """)
    
    questions = {
        'lifestyle': {
            'question': "What best describes your daily activities?",
            'options': [
                "Corporate office work",
                "Creative/casual workplace",
                "Active/on-the-go",
                "Work from home",
                "Mix of formal and casual"
            ]
        },
        'climate': {
            'question': "What's your primary climate?",
            'options': [
                "Four distinct seasons",
                "Mostly warm/hot",
                "Mostly cool/cold",
                "Mild year-round",
                "Extreme temperature changes"
            ]
        },
        'priorities': {
            'question': "What's most important in your clothing?",
            'options': [
                "Comfort and practicality",
                "Professional appearance",
                "Style and fashion",
                "Versatility",
                "Durability"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"essentials_{key}"
        )
        st.markdown("---")
    
    if st.button("Get My Essentials List", type="primary"):
        essentials = analyze_wardrobe_essentials(responses)
        show_wardrobe_essentials_results(essentials)

def analyze_wardrobe_essentials(responses):
    """Analyze quiz responses to determine wardrobe essentials"""
    prompt = f"""Based on these factors:
    Lifestyle: {responses['lifestyle']}
    Climate: {responses['climate']}
    Priorities: {responses['priorities']}
    
    Create a list of 10 essential wardrobe pieces that would best serve this person.
    Return the list with each item on a new line."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a wardrobe planning expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().split('\n')

def show_wardrobe_essentials_results(essentials):
    """Display wardrobe essentials results"""
    st.success("Your Wardrobe Essentials")
    
    st.markdown("### Must-Have Pieces")
    for i, item in enumerate(essentials, 1):
        st.markdown(f"{i}. {item}")
    
    st.markdown("### Building Your Wardrobe")
    st.markdown("""
        Tips for collecting your essentials:
        - Focus on quality over quantity
        - Choose versatile pieces that work together
        - Consider your color palette
        - Invest in good basics first
        - Add statement pieces gradually
    """)
    
    # Check against current wardrobe
    user_clothing = load_user_clothing()
    if not user_clothing.empty:
        st.markdown("### Wardrobe Gap Analysis")
        missing_items = []
        for essential in essentials:
            # Check if any similar items exist in wardrobe
            if not any(essential.lower() in item.lower() for item in user_clothing['name']):
                missing_items.append(essential)
        
        if missing_items:
            st.markdown("#### Items to Consider Adding:")
            for item in missing_items:
                st.markdown(f"- {item}")
        else:
            st.success("You have items matching all the essentials!")

def analyze_colors_with_imagga(image_bytes):
    """Analyze image colors using Imagga API"""
    api_key = os.getenv("IMAGGA_API_KEY")
    api_secret = os.getenv("IMAGGA_API_SECRET")
    
    if not api_key or not api_secret:
        st.error("Imagga API credentials not found. Please check your .env file.")
        return None
    
    try:
        # Imagga API endpoint for color analysis
        api_url = "https://api.imagga.com/v2/colors"
        
        # Prepare the image file for upload
        files = {'image': image_bytes}
        
        # Make API request
        response = requests.post(
            api_url,
            auth=(api_key, api_secret),
            files=files
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error from Imagga API: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error accessing Imagga API: {str(e)}")
        return None

def determine_color_season(colors_data):
    """Use GPT-4 to determine color season based on Imagga color analysis"""
    try:
        if not colors_data or 'result' not in colors_data:
            return None
            
        # Extract dominant colors and their properties
        colors = colors_data['result']['colors']
        
        # Format color data for GPT-4
        color_info = {
            'background_colors': [{'hex': c['html_code'], 'percent': c['percent']} 
                                for c in colors.get('background_colors', [])],
            'foreground_colors': [{'hex': c['html_code'], 'percent': c['percent']} 
                                for c in colors.get('foreground_colors', [])],
            'image_colors': [{'hex': c['html_code'], 'percent': c['percent']} 
                            for c in colors.get('image_colors', [])]
        }
        
        prompt = f"""Based on this color analysis of a person's photo:
        
        Dominant colors (hex codes and percentages):
        {json.dumps(color_info, indent=2)}
        
        Please determine:
        1. Their likely color season (Spring, Summer, Autumn, or Winter)
        2. Whether they have warm or cool undertones
        3. A list of 5-7 colors that would be most flattering for them
        
        Return your response in this exact JSON format:
        {{
            "season": "Season name",
            "undertone": "Warm or Cool",
            "flattering_colors": ["color1", "color2", "etc"],
            "explanation": "Brief explanation of the analysis"
        }}"""
        
        messages = [
            {"role": "system", "content": "You are a color analysis expert."},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages
            )
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError as e:
                st.error(f"Error parsing response: {str(e)}")
                return None
        except Exception as e:
            st.error(f"Error calling GPT-4 API: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"Error processing color data: {str(e)}")
        return None

def face_shape_quiz():
    """Quiz to determine user's face shape"""
    st.markdown("### 👤 Face Shape Analysis")
    st.markdown("""
        Understanding your face shape helps you choose the most flattering:
        - Hairstyles
        - Glasses frames
        - Necklines
        - Accessories
    """)
    
    questions = {
        'face_length': {
            'question': "How would you describe your face length?",
            'options': [
                "Longer than it is wide",
                "About equal in length and width",
                "Wider than it is long"
            ]
        },
        'jaw_shape': {
            'question': "Which best describes your jaw?",
            'options': [
                "Angular and sharp",
                "Rounded",
                "Square and prominent",
                "Narrow and pointed"
            ]
        },
        'cheekbones': {
            'question': "How would you describe your cheekbones?",
            'options': [
                "High and prominent",
                "Round and full",
                "Not very prominent",
                "Wide and angular"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"face_{key}"
        )
        st.markdown("---")
    
    if st.button("Determine My Face Shape", type="primary"):
        face_shape = analyze_face_shape(responses)
        show_face_shape_results(face_shape)

def body_type_quiz():
    """Quiz to determine user's body type"""
    st.markdown("### 📏 Body Type Analysis")
    st.markdown("""
        Understanding your body type helps you:
        - Choose flattering silhouettes
        - Balance your proportions
        - Create harmonious outfits
    """)
    
    questions = {
        'shoulders': {
            'question': "How would you describe your shoulders?",
            'options': [
                "Broader than my hips",
                "Same width as my hips",
                "Narrower than my hips",
                "Angular and straight"
            ]
        },
        'waist': {
            'question': "How defined is your waist?",
            'options': [
                "Very defined/curved",
                "Somewhat defined",
                "Straight with little definition",
                "Not visible/undefined"
            ]
        },
        'body_lines': {
            'question': "Which best describes your overall body lines?",
            'options': [
                "Curved and rounded",
                "Straight and angular",
                "Mixed curved and straight",
                "Soft and undefined"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"body_{key}"
        )
        st.markdown("---")
    
    if st.button("Analyze My Body Type", type="primary"):
        body_type = analyze_body_type(responses)
        show_body_type_results(body_type)

def analyze_face_shape(responses):
    """Analyze quiz responses to determine face shape"""
    prompt = f"""Based on these characteristics:
    Face length: {responses['face_length']}
    Jaw shape: {responses['jaw_shape']}
    Cheekbones: {responses['cheekbones']}
    
    Determine the person's face shape (Oval, Round, Square, Heart, Diamond, or Rectangle).
    Return ONLY the face shape name."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a face shape analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_face_shape_results(face_shape):
    """Display face shape analysis results"""
    st.success(f"Your Face Shape: {face_shape}")
    st.markdown(get_face_shape_tips(face_shape))

def get_face_shape_tips(face_shape):
    """Get styling tips for a face shape"""
    tips = {
        "Oval": "Lucky you! Most styles work well with your balanced proportions.",
        "Round": "Choose angular frames and accessories to add definition.",
        "Square": "Soften angles with curved lines and oval shapes.",
        "Heart": "Balance a wider forehead with wider bottom frames.",
        "Diamond": "Highlight your cheekbones with upswept frames.",
        "Rectangle": "Add width with round or square shapes."
    }
    return tips.get(face_shape, "No specific tips available for this face shape.")

def get_season_tips(season):
    """Get styling tips for a color season"""
    tips = {
        "Warm Spring": """
            - Wear warm, clear colors
            - Choose golden jewelry
            - Avoid dark, cool colors
            - Best neutrals are camel and warm brown
        """,
        "Cool Winter": """
            - Wear clear, cool colors
            - Choose silver jewelry
            - Avoid muted, warm colors
            - Best neutrals are navy and gray
        """,
        # Add other seasons as needed
    }
    return tips.get(season, "No specific tips available for this season.")

# Fix 1: Add missing function for analyzing body type
def analyze_body_type(responses):
    """Analyze quiz responses to determine body type"""
    prompt = f"""Based on these characteristics:
    Shoulders: {responses['shoulders']}
    Waist: {responses['waist']}
    Body lines: {responses['body_lines']}
    
    Determine the person's body type (Hourglass, Rectangle, Triangle, Inverted Triangle, or Oval).
    Return ONLY the body type name."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a body type analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Fix 2: Add missing function for showing body type results
def show_body_type_results(body_type):
    """Display body type analysis results"""
    st.success(f"Your Body Type: {body_type}")
    
    tips = {
        "Hourglass": """
            - Emphasize your natural waist
            - Choose fitted clothing that follows your curves
            - Belt dresses and tops to highlight your waist
            - Avoid boxy or oversized styles
        """,
        "Rectangle": """
            - Create curves with peplum tops and wrap dresses
            - Use belts to define your waist
            - Layer pieces to add dimension
            - Try ruffles and gathered details
        """,
        "Triangle": """
            - Draw attention upward with detailed tops
            - Choose A-line skirts and dresses
            - Opt for darker colors on bottom
            - Balance with structured shoulders
        """,
        "Inverted Triangle": """
            - Balance shoulders with fuller skirts
            - Choose V-necks and scoop necklines
            - Add volume to lower body
            - Avoid shoulder pads and puffy sleeves
        """,
        "Oval": """
            - Create vertical lines to elongate
            - Choose flowing fabrics
            - Wear empire waist styles
            - Focus on structured pieces
        """
    }
    
    st.markdown("### Styling Tips")
    st.markdown(tips.get(body_type, "No specific tips available for this body type."))

# Fix 3: Add missing function for style personality quiz
def style_personality_quiz():
    """Quiz to determine user's style personality"""
    st.markdown("### 👗 Style Personality Quiz")
    st.markdown("""
        Discover your unique style personality! This comprehensive quiz analyzes your preferences
        across multiple dimensions to help you understand and develop your personal style.
    """)
    
    questions = {
        'weekend_style': {
            'question': "What's your ideal weekend outfit?",
            'options': [
                "Comfortable athleisure (leggings, oversized sweater, sneakers)",
                "Polished casual (well-fitted jeans, blazer, loafers)",
                "Bold, artistic ensembles (mixed patterns, unique pieces)",
                "Classic, timeless basics (white shirt, tailored pants)",
                "Trendy, fashion-forward looks (latest styles, statement pieces)"
            ]
        },
        'color_approach': {
            'question': "How do you approach color in your wardrobe?",
            'options': [
                "Neutral palette with occasional pops of color",
                "Bold, vibrant colors that make a statement",
                "Soft, muted tones that blend together",
                "Monochromatic looks in varying shades",
                "Mix of bright and neutral depending on mood"
            ]
        },
        'accessories': {
            'question': "How do you approach accessories?",
            'options': [
                "Minimal and practical (simple watch, studs)",
                "Classic and coordinated (pearls, matching sets)",
                "Bold statement pieces (chunky jewelry, unique designs)",
                "Vintage or artistic pieces with history",
                "Latest trends and modern designs"
            ]
        },
        'shopping': {
            'question': "What's your shopping style?",
            'options': [
                "Quality basics that last years",
                "Investment pieces from luxury brands",
                "Unique, artistic pieces from boutiques",
                "Mix of vintage and contemporary",
                "Latest trends from fashion retailers"
            ]
        },
        'outfit_planning': {
            'question': "How do you approach outfit planning?",
            'options': [
                "Carefully coordinated the night before",
                "Capsule wardrobe with easy mixing",
                "Spontaneous based on mood",
                "Following specific style rules",
                "Inspired by current trends"
            ]
        },
        'style_icons': {
            'question': "Which style icon's aesthetic most resonates with you?",
            'options': [
                "Audrey Hepburn (timeless elegance)",
                "Kate Moss (effortless cool)",
                "Iris Apfel (bold maximalism)",
                "Steve Jobs (minimal uniformity)",
                "Rihanna (fearless experimentation)"
            ]
        },
        'comfort_vs_style': {
            'question': "How do you balance comfort and style?",
            'options': [
                "Comfort is my top priority",
                "Equal balance of both",
                "Style first, but must be wearable",
                "Willing to sacrifice comfort for look",
                "Depends on the occasion"
            ]
        },
        'pattern_preference': {
            'question': "What's your approach to patterns and prints?",
            'options': [
                "Minimal patterns, prefer solid colors",
                "Classic patterns (stripes, checks)",
                "Bold, artistic prints",
                "Mix of patterns and textures",
                "Trendy seasonal patterns"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"style_personality_{key}"
        )
        st.markdown("---")
    
    if st.button("Discover My Style Personality", type="primary"):
        personality = analyze_style_personality(responses)
        show_style_personality_results(personality)

def analyze_style_personality(responses):
    """Enhanced analysis of quiz responses to determine style personality"""
    prompt = f"""Based on these detailed style preferences:
    Weekend style: {responses['weekend_style']}
    Color approach: {responses['color_approach']}
    Accessories: {responses['accessories']}
    Shopping: {responses['shopping']}
    Outfit planning: {responses['outfit_planning']}
    Style icons: {responses['style_icons']}
    Comfort vs style: {responses['comfort_vs_style']}
    Pattern preference: {responses['pattern_preference']}
    
    Analyze these responses to determine the person's primary and secondary style personalities.
    Consider these style types:
    - Classic (timeless, polished, coordinated)
    - Romantic (feminine, soft, detailed)
    - Creative (artistic, unique, experimental)
    - Minimalist (clean, simple, modern)
    - Trendy (current, fashion-forward)
    - Dramatic (bold, statement-making)
    - Natural (comfortable, casual, effortless)
    - Elegant (sophisticated, refined, luxurious)
    
    Return the result in this format:
    Primary: [Style Type]
    Secondary: [Style Type]
    Key Characteristics: [3-4 key traits]"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert fashion psychologist specializing in personal style analysis."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_style_personality_results(personality_analysis):
    """Enhanced display of style personality results"""
    # Parse the analysis
    lines = personality_analysis.split('\n')
    primary = lines[0].split(': ')[1]
    secondary = lines[1].split(': ')[1]
    characteristics = lines[2].split(': ')[1]
    
    # Display results
    st.success("Your Style Analysis Complete!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            ### Primary Style: {primary}
            This is your dominant style preference and should guide most of your wardrobe choices.
        """)
    
    with col2:
        st.markdown(f"""
            ### Secondary Style: {secondary}
            This style influence adds depth and versatility to your primary style.
        """)
    
    st.markdown("### Key Characteristics")
    st.markdown(characteristics)
    
    # Style recommendations based on combination
    st.markdown("### Personalized Style Recommendations")
    
    recommendations = get_style_recommendations(primary, secondary)
    
    tabs = st.tabs(["Wardrobe Essentials", "Color Palette", "Styling Tips", "Shopping Guide"])
    
    with tabs[0]:
        st.markdown("#### Must-Have Pieces")
        for item in recommendations['essentials']:
            st.markdown(f"- {item}")
    
    with tabs[1]:
        st.markdown("#### Your Ideal Color Palette")
        st.markdown(recommendations['colors'])
    
    with tabs[2]:
        st.markdown("#### Styling Tips")
        for tip in recommendations['styling_tips']:
            st.markdown(f"- {tip}")
    
    with tabs[3]:
        st.markdown("#### Shopping Recommendations")
        st.markdown(recommendations['shopping_guide'])
    
    # Action steps
    st.markdown("### Next Steps")
    st.markdown("""
        1. Review your current wardrobe against these recommendations
        2. Identify gaps in your wardrobe essentials
        3. Plan your next shopping trip based on the guidelines
        4. Experiment with combining your primary and secondary styles
    """)

def get_style_recommendations(primary, secondary):
    """Get detailed style recommendations based on style combination"""
    prompt = f"""Create detailed style recommendations for someone with:
    Primary Style: {primary}
    Secondary Style: {secondary}
    
    Include:
    1. List of 10 wardrobe essentials
    2. Ideal color palette description
    3. 5 specific styling tips
    4. Shopping guide with specific store recommendations
    
    Format as a JSON with keys: essentials, colors, styling_tips, shopping_guide"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a professional fashion stylist creating personalized recommendations."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

def wardrobe_essentials_quiz():
    """Quiz to determine essential pieces for user's lifestyle"""
    st.markdown("### 👔 Wardrobe Essentials Quiz")
    st.markdown("""
        Let's identify the key pieces you need based on your lifestyle and preferences.
        This will help you build a functional and versatile wardrobe.
    """)
    
    questions = {
        'lifestyle': {
            'question': "What best describes your daily activities?",
            'options': [
                "Corporate office work",
                "Creative/casual workplace",
                "Active/on-the-go",
                "Work from home",
                "Mix of formal and casual"
            ]
        },
        'climate': {
            'question': "What's your primary climate?",
            'options': [
                "Four distinct seasons",
                "Mostly warm/hot",
                "Mostly cool/cold",
                "Mild year-round",
                "Extreme temperature changes"
            ]
        },
        'priorities': {
            'question': "What's most important in your clothing?",
            'options': [
                "Comfort and practicality",
                "Professional appearance",
                "Style and fashion",
                "Versatility",
                "Durability"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"essentials_{key}"
        )
        st.markdown("---")
    
    if st.button("Get My Essentials List", type="primary"):
        essentials = analyze_wardrobe_essentials(responses)
        show_wardrobe_essentials_results(essentials)

def analyze_wardrobe_essentials(responses):
    """Analyze quiz responses to determine wardrobe essentials"""
    prompt = f"""Based on these factors:
    Lifestyle: {responses['lifestyle']}
    Climate: {responses['climate']}
    Priorities: {responses['priorities']}
    
    Create a list of 10 essential wardrobe pieces that would best serve this person.
    Return the list with each item on a new line."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a wardrobe planning expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().split('\n')

def show_wardrobe_essentials_results(essentials):
    """Display wardrobe essentials results"""
    st.success("Your Wardrobe Essentials")
    
    st.markdown("### Must-Have Pieces")
    for i, item in enumerate(essentials, 1):
        st.markdown(f"{i}. {item}")
    
    st.markdown("### Building Your Wardrobe")
    st.markdown("""
        Tips for collecting your essentials:
        - Focus on quality over quantity
        - Choose versatile pieces that work together
        - Consider your color palette
        - Invest in good basics first
        - Add statement pieces gradually
    """)
    
    # Check against current wardrobe
    user_clothing = load_user_clothing()
    if not user_clothing.empty:
        st.markdown("### Wardrobe Gap Analysis")
        missing_items = []
        for essential in essentials:
            # Check if any similar items exist in wardrobe
            if not any(essential.lower() in item.lower() for item in user_clothing['name']):
                missing_items.append(essential)
        
        if missing_items:
            st.markdown("#### Items to Consider Adding:")
            for item in missing_items:
                st.markdown(f"- {item}")
        else:
            st.success("You have items matching all the essentials!")

def get_color_analysis(skin_hex, hair_hex, eye_hex):
    """Get color analysis from GPT-4"""
    prompt = f"""Analyze these colors for seasonal color analysis:
    Skin Tone: {skin_hex}
    Hair Color: {hair_hex}
    Eye Color: {eye_hex}
    
    Determine the person's color season (Spring, Summer, Autumn, or Winter) 
    and provide specific color recommendations.
    
    Return the response in this JSON format:
    {{
        "season": "The determined season",
        "explanation": "Why this season was chosen",
        "best_colors": ["color1", "color2", "color3", ...],
        "avoid_colors": ["color1", "color2", "color3", ...],
        "makeup_tips": "Makeup recommendations",
        "jewelry": "Metal and jewelry recommendations"
    }}"""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert color analyst."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

def show_color_analysis_results(analysis):
    """Display color analysis results"""
    st.success(f"Your Color Season: {analysis['season']}")
    
    # Create tabs for different aspects of the analysis
    tabs = st.tabs(["Overview", "Best Colors", "Colors to Avoid", "Makeup", "Jewelry"])
    
    with tabs[0]:
        st.markdown("### Understanding Your Colors")
        st.markdown(analysis['explanation'])
        
    with tabs[1]:
        st.markdown("### Colors That Enhance Your Natural Beauty")
        for color in analysis['best_colors']:
            st.markdown(f"""
                <div style='
                    background-color: {color}; 
                    padding: 10px; 
                    margin: 5px; 
                    border-radius: 5px;
                    color: white;
                    text-shadow: 1px 1px 1px rgba(0,0,0,0.5);'>
                    {color}
                </div>
            """, unsafe_allow_html=True)
            
    with tabs[2]:
        st.markdown("### Colors to Avoid")
        for color in analysis['avoid_colors']:
            st.markdown(f"""
                <div style='
                    background-color: {color}; 
                    padding: 10px; 
                    margin: 5px; 
                    border-radius: 5px;
                    color: white;
                    text-shadow: 1px 1px 1px rgba(0,0,0,0.5);'>
                    {color}
                </div>
            """, unsafe_allow_html=True)
            
    with tabs[3]:
        st.markdown("### Makeup Recommendations")
        st.markdown(analysis['makeup_tips'])
        
    with tabs[4]:
        st.markdown("### Jewelry Recommendations")
        st.markdown(analysis['jewelry'])

def get_season_colors(season):
    """Get recommended and avoid colors for a season"""
    color_recommendations = {
        "Warm Spring": {
            "recommended": [
                "Warm Yellow",
                "Coral",
                "Peach",
                "Warm Green",
                "Golden Brown"
            ],
            "avoid": [
                "Deep Purple",
                "Cool Gray",
                "Black",
                "Navy Blue",
                "Cool Pink"
            ]
        },
        "Cool Summer": {
            "recommended": [
                "Soft Pink",
                "Powder Blue",
                "Lavender",
                "Sage Green",
                "Cool Gray"
            ],
            "avoid": [
                "Orange",
                "Bright Yellow",
                "Tomato Red",
                "Warm Brown",
                "Gold"
            ]
        },
        "Warm Autumn": {
            "recommended": [
                "Rust",
                "Olive Green",
                "Warm Brown",
                "Terracotta",
                "Bronze"
            ],
            "avoid": [
                "Cool Pink",
                "Ice Blue",
                "Pure White",
                "Cool Purple",
                "Silver"
            ]
        },
        "Cool Winter": {
            "recommended": [
                "Pure White",
                "Navy Blue",
                "Cool Red",
                "Royal Purple",
                "Ice Pink"
            ],
            "avoid": [
                "Orange",
                "Warm Brown",
                "Olive Green",
                "Coral",
                "Gold"
            ]
        }
    }
    
    # If the exact season isn't found, return default colors
    if season not in color_recommendations:
        return {
            "recommended": ["Navy", "Gray", "White", "Black", "Blue"],
            "avoid": ["Neon Colors", "Very Bright Colors", "Clashing Colors"]
        }
    
    return color_recommendations[season]

def get_color_info(color):
    """Get color information from a hex code or color name"""
    try:
        # If color is a name, convert to hex
        if not color.startswith('#'):
            # Make API request to convert name to hex
            url = f"https://www.thecolorapi.com/id?name={color}&format=json"
            response = requests.get(url)
            data = response.json()
            hex_code = data['hex']['value']
            name = color
        else:
            # Color is already hex, get name from API
            hex_code = color
            url = f"https://www.thecolorapi.com/id?hex={color.lstrip('#')}&format=json"
            response = requests.get(url)
            data = response.json()
            name = data['name']['value']
        
        return {
            'hex': hex_code,
            'name': name,
            'rgb': data['rgb']['value'],
            'hsl': data['hsl']['value']
        }
    except Exception as e:
        st.error(f"Error getting color information: {str(e)}")
        return {
            'hex': color,
            'name': color,
            'rgb': color,
            'hsl': color
        }

def get_image_colors(image_bytes):
    """Extract colors from image using Imagga API"""
    # Imagga API credentials
    api_key = st.secrets["IMAGGA_API_KEY"]
    api_secret = st.secrets["IMAGGA_API_SECRET"]
    
    # API endpoint
    url = "https://api.imagga.com/v2/colors"
    
    # Request headers
    headers = {
        'accept': 'application/json',
        'authorization': f'Basic {api_key}:{api_secret}'
    }
    
    # Upload image
    files = {'image': image_bytes}
    
    try:
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        
        if response.status_code == 200:
            colors = data['result']['colors']
            
            # Extract dominant colors
            background_colors = colors.get('background_colors', [])
            foreground_colors = colors.get('foreground_colors', [])
            image_colors = colors.get('image_colors', [])
            
            # Return all color information
            return {
                'background': background_colors,
                'foreground': foreground_colors,
                'image': image_colors
=======
def weather_based_outfits():
    st.title("Weather-Based Outfit Suggestions 🌤️")
    
    # Get user's location
    location = st.text_input("Enter your city", "San Francisco")
    
    if location:
        try:
            # Get weather data (you'll need to implement this with a weather API)
            weather_data = {
                "temperature": 72,
                "condition": "sunny",
                "humidity": 65
>>>>>>> 7b3a50d0eb23e94ce0899f6752bbb7768815a0da
            }
            
            # Display weather info
            st.markdown(f"""
                ### Current Weather in {location}
                Temperature: {weather_data['temperature']}°F
                Condition: {weather_data['condition'].title()}
                Humidity: {weather_data['humidity']}%
            """)
            
            # Load user's clothes
            user_clothing = load_user_clothing()
            
            if not user_clothing.empty:
                # Get outfit suggestion based on weather
                prompt = f"""
                Suggest an outfit for {weather_data['temperature']}°F, {weather_data['condition']} weather.
                Available clothes:
                {user_clothing[['name', 'type_of_clothing', 'color']].to_string()}
                """
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a fashion expert suggesting weather-appropriate outfits."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                st.markdown("### Suggested Outfit")
                st.markdown(response.choices[0].message.content)
                
                # Option to save the outfit
                if st.button("Save this outfit"):
                    # Implementation for saving the outfit
                    st.success("Outfit saved!")
            else:
                st.info("Add some clothes to get weather-based outfit suggestions!")
        except Exception as e:
            st.error(f"Error getting weather data: {str(e)}")

def schedule_outfits():
    st.title("Outfit Calendar 📅")
    
    # Date selection
    selected_date = st.date_input("Select a date")
    
    # Load user's clothes and existing outfits
    user_clothing = load_user_clothing()
    outfits_file = f"{st.session_state.username}_outfits.json"
    
    if user_clothing.empty:
        st.info("Add some clothes to start planning outfits!")
        return
    
    # Load existing outfits
    if os.path.exists(outfits_file):
        with open(outfits_file, 'r') as f:
            outfits = json.load(f)
    else:
        outfits = []
    
    # Create new outfit
    st.markdown("### Create Outfit for Selected Date")
    
    # Select clothes for the outfit
    selected_items = st.multiselect(
        "Select clothes for this outfit",
        options=user_clothing['name'].tolist()
    )
    
    occasion = st.selectbox(
        "Occasion",
        ["Casual", "Business", "Formal", "Party", "Sport", "Beach"]
    )
    
    if selected_items:
        # Display selected items
        cols = st.columns(len(selected_items))
        for idx, item_name in enumerate(selected_items):
            item = user_clothing[user_clothing['name'] == item_name].iloc[0]
            with cols[idx]:
                if os.path.exists(item['image_path']):
                    st.image(item['image_path'], use_column_width=True)
                st.markdown(f"**{item['name']}**")
        
        # Save outfit
        if st.button("Schedule Outfit"):
            outfit_name = f"Outfit {selected_date.strftime('%Y%m%d')}"
            
            # Create outfit object
            new_outfit = {
                "id": str(uuid.uuid4()),
                "name": outfit_name,
                "items": [
                    {
                        "name": item_name,
                        "image_path": user_clothing[user_clothing['name'] == item_name].iloc[0]['image_path'],
                        "type_of_clothing": user_clothing[user_clothing['name'] == item_name].iloc[0]['type_of_clothing'],
                        "color": user_clothing[user_clothing['name'] == item_name].iloc[0]['color']
                    }
                    for item_name in selected_items
                ],
                "occasion": occasion,
                "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Add to outfits list
            outfits.append(new_outfit)
            
            # Save to file
            with open(outfits_file, 'w') as f:
                json.dump(outfits, f, indent=2)
            
            st.success(f"Outfit scheduled for {selected_date}")
            st.rerun()

def style_quizzes():
    st.title("Style Quizzes 📝")
    
    quiz_type = st.selectbox(
        "Choose a quiz",
        ["Color Season Analysis", "Style Personality", "Body Type Guide"]
    )
    
    if quiz_type == "Color Season Analysis":
        st.markdown("### Discover Your Color Season")
        
        skin_tone = st.selectbox(
            "What's your skin undertone?",
            ["Warm", "Cool", "Neutral"]
        )
        
        hair_color = st.selectbox(
            "What's your natural hair color?",
            ["Black", "Brown", "Blonde", "Red", "Gray"]
        )
        
        eye_color = st.selectbox(
            "What's your eye color?",
            ["Brown", "Blue", "Green", "Hazel", "Gray"]
        )
        
        if st.button("Analyze My Season"):
            # This would typically involve more complex analysis
            season = "Winter"  # Placeholder
            st.markdown(f"### Your Color Season: {season}")
            # Add season-specific advice
    
    elif quiz_type == "Style Personality":
        st.markdown("### Discover Your Style Personality")
        
        # Add style personality quiz questions
        pass
    
    else:  # Body Type Guide
        st.markdown("### Find Your Body Type")
        
        # Add body type quiz questions
        pass

def display_saved_outfits():
    st.title("Your Saved Outfits 👔")
    
    # Load user's outfits from JSON file
    outfits_file = f"{st.session_state.username}_outfits.json"
    
    if not os.path.exists(outfits_file):
        st.info("No outfits saved yet! Create your first outfit to get started.")
        if st.button("Create Outfit"):
            st.query_params["page"] = "Outfit Calendar"
            st.rerun()
        return
    
    try:
        with open(outfits_file, 'r') as f:
            outfits = json.load(f)
        
        if not outfits:
            st.info("No outfits saved yet! Create your first outfit to get started.")
            return
        
        # Filter options
        occasions = sorted(set(outfit['occasion'] for outfit in outfits))
        selected_occasion = st.selectbox("Filter by occasion", ["All"] + occasions)
        
        # Filter outfits by occasion
        filtered_outfits = outfits
        if selected_occasion != "All":
            filtered_outfits = [outfit for outfit in outfits if outfit['occasion'] == selected_occasion]
        
        # Display outfits in a grid
        for outfit in filtered_outfits:
            with st.container():
                st.markdown(f"""
                    <div style='padding: 20px; background-color: rgba(44, 62, 80, 0.1); 
                         border-radius: 10px; margin-bottom: 20px;'>
                    <h3 style='color: #2c3e50;'>{outfit['name']}</h3>
                    <p><em>Occasion: {outfit['occasion']}</em></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display outfit items in a row
                cols = st.columns(len(outfit['items']))
                for idx, item in enumerate(outfit['items']):
                    with cols[idx]:
                        if os.path.exists(item['image_path']):
                            st.image(item['image_path'], caption=item['name'])
                        st.markdown(f"""
                            **{item['name']}**  
                            Type: {item.get('type_of_clothing', 'N/A')}  
                            Color: {item.get('color', 'N/A')}
                        """)
                
                # Delete outfit button
                if st.button(f"Delete {outfit['name']}", key=f"delete_outfit_{outfit['id']}"):
                    outfits.remove(outfit)
                    with open(outfits_file, 'w') as f:
                        json.dump(outfits, f, indent=2)
                    st.success(f"Deleted outfit: {outfit['name']}")
                    st.rerun()
                
                st.markdown("---")
                
    except Exception as e:
        st.error(f"Error loading outfits: {str(e)}")

def main():
    set_custom_style()
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "show_style_quiz" not in st.session_state:
        st.session_state.show_style_quiz = False

    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50; padding: 2rem 0;'>
            👔 Your Digital Wardrobe
        </h1>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in and st.session_state.username:
        if st.session_state.show_style_quiz:
            style_quiz()
        elif st.session_state.get('show_tutorial', False):
            show_tutorial()
        else:
            # Regular app flow
            migrate_images()
            
            # Get page from URL parameters
            current_page = st.query_params.get('page', 'Home')
            
            # Update sidebar to match URL
            page = st.sidebar.selectbox(
                "Choose a page",
                ["Home", "Image Uploader and Display", "Saved Clothes", 
                 "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
                 "Saved Outfits", "Outfit Calendar", "Style Quizzes", "AI Shopping Assistant"],
                index=["Home", "Image Uploader and Display", "Saved Clothes", 
                       "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
                       "Saved Outfits", "Outfit Calendar", "Style Quizzes", "AI Shopping Assistant"].index(current_page)
            )
            
            # Show the selected page
            if page == "Home":
                homepage()
            elif page == "Image Uploader and Display":
                image_uploader_and_display()
            elif page == "Saved Clothes":
                display_saved_clothes()
            elif page == "Clothing Data Insights with GPT-4":
                clothing_data_insights()
            elif page == "Weather-Based Outfits":
                weather_based_outfits()
            elif page == "Saved Outfits":
                display_saved_outfits()
            elif page == "Outfit Calendar":
                schedule_outfits()
            elif page == "Style Quizzes":
                style_quizzes()
            elif page == "AI Shopping Assistant":
                suggest_internet_clothes()
=======
import os
from src.auth.auth_handlers import (
    login, create_account, verify_user
)
from src.weather.weather_service import weather_based_outfits
from src.wardrobe.clothing_manager import (
    display_saved_clothes, clothing_data_insights,
    image_uploader_and_display
)
from src.wardrobe.outfit_manager import (
    display_saved_outfits, schedule_outfits
)
from src.quizzes.quiz_handlers import style_quizzes

def set_custom_style():
    st.markdown("""
        <style>
        /* Global Styles */
        .stApp {
            background-color: #FDFBF9;
            font-family: 'Playfair Display', serif;
            color: #2C1810;
        }
        
        /* Sidebar Background */
        section[data-testid="stSidebar"] > div {
            background-color: #2C1810;
        }
        
        /* All Sidebar Text */
        section[data-testid="stSidebar"] * {
            color: white !important;
        }

        /* Authentication Dropdown */
        section[data-testid="stSidebar"] .st-emotion-cache-1629p8f {
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .st-emotion-cache-1629p8f * {
            color: white !important;
        }
        
        section[data-testid="stSidebar"] .st-emotion-cache-16idsys {
            color: white !important;
        }

        section[data-testid="stSidebar"] .st-emotion-cache-16idsys p {
            color: white !important;
        }

        /* Authentication Title */
        section[data-testid="stSidebar"] .st-emotion-cache-16idsys label {
            color: white !important;
        }

        /* Sidebar Dropdown Specific Styles */
        section[data-testid="stSidebar"] [data-baseweb="select"] {
            background-color: #2C1810 !important;
        }
        
        section[data-testid="stSidebar"] [data-baseweb="select"] * {
            color: white !important;
            background-color: #2C1810 !important;
        }
        
        section[data-testid="stSidebar"] [data-baseweb="popover"] * {
            color: white !important;
            background-color: #2C1810 !important;
        }
        
        section[data-testid="stSidebar"] [role="listbox"] {
            background-color: #2C1810 !important;
        }
        
        section[data-testid="stSidebar"] [role="option"] {
            color: white !important;
            background-color: #2C1810 !important;
        }
        
        section[data-testid="stSidebar"] [role="option"]:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* Sidebar Dropdown Value */
        section[data-testid="stSidebar"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
            color: white !important;
        }

        /* Sidebar Dropdown Arrow */
        section[data-testid="stSidebar"] [data-baseweb="icon"] {
            color: white !important;
        }

        /* Ensure dropdown options remain white */
        section[data-testid="stSidebar"] .st-emotion-cache-1oe5cao {
            color: white !important;
            background-color: #2C1810 !important;
        }

        section[data-testid="stSidebar"] .st-emotion-cache-1oe5cao:hover {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }

        /* Dropdown container background */
        section[data-testid="stSidebar"] .st-emotion-cache-b0tbah {
            background-color: #2C1810 !important;
        }

        /* Selected option in dropdown */
        section[data-testid="stSidebar"] .st-emotion-cache-16idsys p {
            color: white !important;
        }

        /* Sidebar Title */
        section[data-testid="stSidebar"] .st-emotion-cache-10trblm {
            color: white !important;
        }

        /* Sidebar Navigation */
        section[data-testid="stSidebar"] .st-emotion-cache-6qob1r {
            color: white !important;
        }

        /* Sidebar Buttons */
        section[data-testid="stSidebar"] button {
            color: white !important;
            border: 1px solid white !important;
            background-color: transparent !important;
        }

        section[data-testid="stSidebar"] button:hover {
            background-color: rgba(255, 255, 255, 0.2) !important;
            color: white !important;
        }

        /* Sidebar Icons */
        section[data-testid="stSidebar"] svg {
            fill: white !important;
        }

        /* Sidebar Labels */
        section[data-testid="stSidebar"] label {
            color: white !important;
        }

        /* Sidebar Dropdown Text */
        section[data-testid="stSidebar"] [data-baseweb="select"] span {
            color: white !important;
        }

        /* Typography */
        h1, h2, h3, p, span, div {
            font-family: 'Playfair Display', serif;
            color: #2C1810;
            letter-spacing: 1px;
        }
        
        h1 {
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 2rem;
            border-bottom: 2px solid #D4B08C;
            padding-bottom: 1rem;
        }
        
        /* Sidebar Buttons */
        .stButton button {
            background-color: #2C1810;
            color: #FDFBF9;
            border: none;
            border-radius: 4px;
            padding: 0.5rem 1.5rem;
            font-family: 'Playfair Display', serif;
            transition: all 0.3s ease;
        }
        
        .stButton button:hover {
            background-color: #D4B08C;
            color: #2C1810;
        }
        
        /* Welcome Message */
        .welcome-msg {
            text-align: center;
            padding: 3rem;
            background: linear-gradient(135deg, rgba(212,176,140,0.1) 0%, rgba(44,24,16,0.05) 100%);
            border-radius: 10px;
            margin: 2rem 0;
            border: 1px solid rgba(212,176,140,0.3);
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            color: #2C1810;
        }
        
        /* Cards and Containers */
        .stMarkdown div {
            border-radius: 8px;
            padding: 1rem;
            color: #2C1810;
        }
        
        /* File Uploader */
        .stUploadedFile {
            background-color: rgba(212,176,140,0.1);
            border: 1px dashed #D4B08C;
            border-radius: 8px;
            padding: 1rem;
            color: #2C1810;
        }
        
        /* Selectbox */
        .stSelectbox div[data-baseweb="select"] {
            background-color: #FDFBF9;
            border: 1px solid #D4B08C;
            color: #2C1810;
        }
        
        /* Text Input */
        .stTextInput input {
            border: 1px solid #D4B08C;
            background-color: #FDFBF9;
            border-radius: 4px;
            color: #2C1810;
        }
        
        /* Labels and Text */
        .stTextInput label, 
        .stSelectbox label,
        .stFileUploader label {
            color: #2C1810 !important;
        }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #FDFBF9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #D4B08C;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #2C1810;
        }
        
        /* Loading Spinner */
        .stSpinner > div {
            border-color: #D4B08C !important;
        }
        </style>
        
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap" rel="stylesheet">
    """, unsafe_allow_html=True)

def main():
<<<<<<< HEAD
   set_custom_style()
  
   if "logged_in" not in st.session_state:
       st.session_state.logged_in = False
   if "username" not in st.session_state:
       st.session_state.username = None
   if "show_style_quiz" not in st.session_state:
       st.session_state.show_style_quiz = False


   st.markdown("""
       <h1 style='text-align: center; color: #2c3e50; padding: 2rem 0;'>
           👔 Your Digital Wardrobe
       </h1>
   """, unsafe_allow_html=True)


   if st.session_state.logged_in and st.session_state.username:
       if st.session_state.show_style_quiz:
           style_quiz()
       elif st.session_state.get('show_tutorial', False):
           show_tutorial()
       else:
           # Regular app flow
           migrate_images()
           
           # Get page from URL parameters
           current_page = st.query_params.get('page', 'Home')
           
           # Update sidebar to match URL
           page = st.sidebar.selectbox(
               "Choose a page",
               ["Home", "Image Uploader and Display", "Saved Clothes", 
                "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
                "Saved Outfits", "Outfit Calendar", "Style Quizzes", 
                "Shopping Recommendations"],  # Added new page
               index=["Home", "Image Uploader and Display", "Saved Clothes", 
                      "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
                      "Saved Outfits", "Outfit Calendar", "Style Quizzes",
                      "Shopping Recommendations"].index(current_page)
           )
           
           # Show the selected page
           if page == "Home":
               homepage()
           elif page == "Image Uploader and Display":
               image_uploader_and_display()
           elif page == "Saved Clothes":
               display_saved_clothes()
           elif page == "Clothing Data Insights with GPT-4":
               clothing_data_insights()
           elif page == "Weather-Based Outfits":
               weather_based_outfits()
           elif page == "Saved Outfits":
               display_saved_outfits()
           elif page == "Outfit Calendar":
               schedule_outfits()
           elif page == "Style Quizzes":
               style_quizzes()
           elif page == "Shopping Recommendations":
               shopping_recommendations()
   else:
       st.markdown("""
           <div class='welcome-msg'>
               Welcome to Your Digital Wardrobe!
               <br>Please login or create an account to get started.
           </div>
       """, unsafe_allow_html=True)
       
       auth_page = st.sidebar.selectbox("Authentication", ["Login", "Create Account"])
       if auth_page == "Login":
           login()
       elif auth_page == "Create Account":
           create_account()
=======
    set_custom_style()
    st.sidebar.title("Navigation")
    
    if "logged_in" in st.session_state and st.session_state.logged_in:
        pages = {
            "Home": "👋",
            "Add Clothes": "👕",
            "Saved Clothes": "👔",
            "Clothing Data Insights": "📊",
            "Weather-Based Outfits": "🌤️",
            "Saved Outfits": "👗",
            "Outfit Calendar": "📅",
            "Style Quizzes": "✨"
        }
        
        page = st.sidebar.selectbox(
            "Choose a page",
            pages.keys(),
            format_func=lambda x: f"{pages[x]} {x}"
        )
        
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
        
        if page == "Home":
            st.title(f"Welcome back, {st.session_state.username}! 👋")
            st.write("Choose a page from the sidebar to get started.")
        elif page == "Add Clothes":
            image_uploader_and_display()
        elif page == "Saved Clothes":
            display_saved_clothes()
        elif page == "Clothing Data Insights":
            clothing_data_insights()
        elif page == "Weather-Based Outfits":
            weather_based_outfits()
        elif page == "Saved Outfits":
            display_saved_outfits()
        elif page == "Outfit Calendar":
            schedule_outfits()
        elif page == "Style Quizzes":
            style_quizzes()
>>>>>>> 82784ae66500dcd327bb26ca80802df0894371fb
    else:
        st.markdown("""
            <div class='welcome-msg'>
                Welcome to Your Digital Wardrobe!
                <br>Please login or create an account to get started.
            </div>
        """, unsafe_allow_html=True)
        
        auth_page = st.sidebar.selectbox("Authentication", ["Login", "Create Account"])
        if auth_page == "Login":
            login()
        elif auth_page == "Create Account":
            create_account()
<<<<<<< HEAD
>>>>>>> 7b3a50d0eb23e94ce0899f6752bbb7768815a0da

# Add these new functions
def shopping_recommendations():
    """Generate personalized shopping recommendations"""
    st.title("🛍️ Personalized Shopping Recommendations")
    
    # Create tabs for different recommendation types
    tab1, tab2, tab3, tab4 = st.tabs([
        "👕 Similar to My Clothes",
        "❓ Based on Questions",
        "👗 Complete an Outfit",
        "💝 My Wishlist"  # New tab
    ])
    
    with tab1:
        similar_clothes_recommendations()
    
    with tab2:
        question_based_recommendations()
    
    with tab3:
        complete_outfit_recommendations()
        
    with tab4:
        view_wishlist()

def view_wishlist():
    """View and manage wishlist items"""
    st.markdown("### My Wishlist")
    
    # Verify user is logged in
    if "username" not in st.session_state:
        st.error("Please log in to view your wishlist.")
        return
        
    wishlist_file = f"{st.session_state.username}_wishlist.json"
    
    # Check if wishlist file exists
    if not os.path.exists(wishlist_file):
        st.info("Your wishlist is empty. Start saving items you like!")
        return
        
    try:
        # Read wishlist file
        with open(wishlist_file, 'r') as f:
            wishlist = json.load(f)
            
        if not wishlist:
            st.info("Your wishlist is empty. Start saving items you like!")
            return
            
        # Add sort options
        sort_by = st.selectbox(
            "Sort by:",
            ["Date Added (Newest)", "Date Added (Oldest)", "Price (Low to High)", "Price (High to Low)"]
        )
        
        # Sort wishlist items
        try:
            if sort_by == "Date Added (Newest)":
                wishlist = sorted(wishlist, key=lambda x: x['date_added'], reverse=True)
            elif sort_by == "Date Added (Oldest)":
                wishlist = sorted(wishlist, key=lambda x: x['date_added'])
            elif sort_by == "Price (Low to High)":
                wishlist = sorted(wishlist, key=lambda x: float(x['item'].get('price', '0').replace('$', '').replace(',', '')))
            elif sort_by == "Price (High to Low)":
                wishlist = sorted(wishlist, key=lambda x: float(x['item'].get('price', '0').replace('$', '').replace(',', '')), reverse=True)
        except (KeyError, ValueError) as e:
            st.warning("Some items may have invalid price data. Sorting might not be accurate.")
        
        # Display items in grid
        for i in range(0, len(wishlist), 3):
            cols = st.columns(3)
            for j, col in enumerate(cols):
                if i + j < len(wishlist):
                    item_data = wishlist[i + j]
                    item = item_data['item']
                    with col:
                        # Display product image
                        if 'thumbnail' in item:
                            st.image(item['thumbnail'], use_column_width=True)
                        
                        # Display product details
                        st.markdown(f"""
                            **{item.get('title', 'No title')[:50]}...**  
                            💰 {item.get('price', 'Price not available')}  
                            {f"⭐ {item.get('rating')} ({item.get('reviews', '0')})" if 'rating' in item else ''}  
                            📅 Added: {item_data['date_added']}
                        """)
                        
                        # Add link to product
                        if 'link' in item:
                            st.markdown(f"[Shop Now]({item['link']})")
                        
                        # Remove from wishlist button
                        if st.button("🗑️ Remove", key=f"remove_{i}_{j}"):
                            wishlist.pop(i + j)
                            with open(wishlist_file, 'w') as f:
                                json.dump(wishlist, f, indent=2)
                            st.experimental_rerun()
        
        # Add export option
        if st.button("📥 Export Wishlist"):
            export_wishlist(wishlist)
            
    except json.JSONDecodeError:
        st.error("Error reading wishlist file. The file may be corrupted.")
    except Exception as e:
        st.error(f"An error occurred while loading your wishlist: {str(e)}")

def export_wishlist(wishlist):
    """Export wishlist to CSV"""
    try:
        # Create DataFrame from wishlist
        data = []
        for item_data in wishlist:
            item = item_data['item']
            data.append({
                'Title': item.get('title', 'No title'),
                'Price': item.get('price', 'N/A'),
                'Rating': item.get('rating', 'N/A'),
                'Reviews': item.get('reviews', 'N/A'),
                'Link': item.get('link', 'N/A'),
                'Date Added': item_data['date_added']
            })
        
        df = pd.DataFrame(data)
        
        # Convert DataFrame to CSV
        csv = df.to_csv(index=False)
        
        # Create download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="wishlist.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error exporting wishlist: {str(e)}")

def save_to_wishlist(item):
    """Save an item to the user's wishlist"""
    if 'username' not in st.session_state:
        st.error("Please log in to save items to your wishlist.")
        return

    wishlist_file = f"{st.session_state.username}_wishlist.json"
    wishlist = []

    try:
        # Load existing wishlist if it exists
        if os.path.exists(wishlist_file):
            with open(wishlist_file, 'r') as f:
                wishlist = json.load(f)

        # Add new item with timestamp
        wishlist.append({
            'item': item,
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # Save updated wishlist
        with open(wishlist_file, 'w') as f:
            json.dump(wishlist, f, indent=2)
            
        st.success("Item added to wishlist!")
        
    except Exception as e:
        st.error(f"Error saving to wishlist: {str(e)}")

def similar_clothes_recommendations():
    """Find clothes similar to user's existing wardrobe"""
    st.markdown("### Find Similar Clothes")
    
    # Load user's wardrobe
    user_clothing = load_user_clothing()
    if user_clothing.empty:
        st.info("Add some clothes to your wardrobe first to get recommendations!")
        return
    
    # Let user select which item to find similar clothes for
    selected_item = st.selectbox(
        "Select an item from your wardrobe to find similar pieces:",
        options=user_clothing['name'].tolist()
    )
    
    if selected_item:
        item_details = user_clothing[user_clothing['name'] == selected_item].iloc[0]
        
        # Show selected item details
        col1, col2 = st.columns([1, 2])
        with col1:
            if os.path.exists(item_details['image_path']):
                st.image(item_details['image_path'], caption="Selected Item")
        
        with col2:
            st.markdown(f"""
                **Type:** {item_details['type_of_clothing']}  
                **Color:** {item_details['color']}  
                **Season:** {item_details['season']}
            """)
        
        # Get similar items using SERP API
        search_query = f"{item_details['color']} {item_details['type_of_clothing']} similar to {selected_item}"
        recommendations = get_shopping_recommendations(search_query, "")
        
        if recommendations:
            st.markdown("### Similar Items You Might Like")
            display_shopping_recommendations(recommendations, "similar")

def question_based_recommendations():
    """Get recommendations based on user's answers to questions"""
    st.markdown("### Find Clothes Based on Your Preferences")
    
    # Questions to help narrow down recommendations
    occasion = st.text_input(
        "What occasion are you shopping for?",
        placeholder="e.g., Casual, Work, Special Event, Workout, Vacation"
    )
    
    budget = st.text_input(
        "What's your budget range?",
        placeholder="e.g., Budget, Mid-range, High-end, Luxury"
    )
    
    style_preference = st.text_input(
        "What styles do you prefer?",
        placeholder="e.g., Classic, Trendy, Bohemian, Minimalist, Streetwear, Elegant"
    )
    
    color_preference = st.color_picker("Choose a color you're looking for:", "#000000")
    
    if st.button("Find Recommendations"):
        if not occasion or not budget or not style_preference:
            st.warning("Please fill in all fields to get personalized recommendations.")
            return
            
        # Construct search query based on answers
        search_query = f"{occasion} {style_preference} clothing {budget}"
        recommendations = get_shopping_recommendations(search_query, "")
        
        if recommendations:
            st.markdown("### Recommended Items")
            display_shopping_recommendations(recommendations, "questions")

def complete_outfit_recommendations():
    """Find items to complete an outfit"""
    st.markdown("### Complete Your Outfit")
    
    # Load user's saved outfits and wardrobe
    outfits = load_saved_outfits()
    user_clothing = load_user_clothing()
    
    if user_clothing.empty:
        st.info("Add some clothes to your wardrobe first to get completion recommendations!")
        return
    
    # Option to start from saved outfit or create new
    start_from = st.radio(
        "How would you like to start?",
        ["Start from a saved outfit", "Build a new outfit"]
    )
    
    if start_from == "Start from a saved outfit":
        if not outfits:
            st.info("Create some outfits first to use this feature!")
            return
            
        # Select saved outfit
        outfit_names = [outfit['name'] for outfit in outfits]
        selected_outfit = st.selectbox("Select an outfit to complete:", outfit_names)
        
        if selected_outfit:
            outfit = next((o for o in outfits if o['name'] == selected_outfit), None)
            if outfit:
                # Display current outfit items
                st.markdown("### Current Outfit Items")
                cols = st.columns(len(outfit['items']))
                for idx, item in enumerate(outfit['items']):
                    with cols[idx]:
                        if os.path.exists(item.get('image_path', '')):
                            st.image(item['image_path'], caption=item.get('name', ''))
                
                # Suggest what's missing
                missing_items = suggest_missing_items(outfit['items'])
                if missing_items:
                    st.markdown("### Suggested Items to Complete the Outfit")
                    for idx, item in enumerate(missing_items):
                        recommendations = get_shopping_recommendations(item, "")
                        if recommendations:
                            st.markdown(f"#### {item}")
                            display_shopping_recommendations(recommendations, f"complete_{idx}")
    
    else:  # Build a new outfit
        # Let user select base items
        st.markdown("### Select Base Items for Your Outfit")
        selected_items = st.multiselect(
            "Choose items from your wardrobe:",
            options=user_clothing['name'].tolist()
        )
        
        if selected_items:
            # Display selected items
            st.markdown("### Selected Items")
            cols = st.columns(len(selected_items))
            items_details = []
            for idx, item_name in enumerate(selected_items):
                item = user_clothing[user_clothing['name'] == item_name].iloc[0]
                items_details.append({
                    'name': item_name,
                    'type_of_clothing': item.get('type_of_clothing') or item.get('type') or item.get('category'),
                    'color': item.get('color', ''),
                    'image_path': item.get('image_path', '')
                })
                with cols[idx]:
                    if os.path.exists(item.get('image_path', '')):
                        st.image(item['image_path'], caption=item_name)
            
            # Suggest completing items
            missing_items = suggest_missing_items(items_details)
            if missing_items:
                st.markdown("### Suggested Items to Complete the Outfit")
                for item in missing_items:
                    recommendations = get_shopping_recommendations(item, "")
                    if recommendations:
                        st.markdown(f"#### {item}")
                        display_shopping_recommendations(recommendations, f"complete_{idx}")

def suggest_missing_items(outfit_items):
    """Suggest items that would complete an outfit"""
    # Extract types of clothing in the outfit, handling different data structures
    current_types = []
    for item in outfit_items:
        # Handle both dictionary and object formats
        if isinstance(item, dict):
            item_type = item.get('type_of_clothing') or item.get('type') or item.get('category')
        else:
            # If item is an object/row from DataFrame
            item_type = getattr(item, 'type_of_clothing', None) or getattr(item, 'type', None) or getattr(item, 'category', None)
        
        if item_type:
            current_types.append(item_type.lower())
    
    # Basic outfit completion rules
    outfit_rules = {
        'tops': ['shirt', 'blouse', 't-shirt', 'sweater', 'top'],
        'bottoms': ['pants', 'skirt', 'shorts', 'jeans'],
        'shoes': ['sneakers', 'boots', 'heels', 'sandals'],
        'accessories': ['necklace', 'earrings', 'bracelet', 'belt'],
        'outerwear': ['jacket', 'coat', 'cardigan']
    }
    
    # Check what's missing
    missing_items = []
    
    # Check for main components
    if not any(type in current_types for type in outfit_rules['tops']):
        missing_items.append("Top")
    if not any(type in current_types for type in outfit_rules['bottoms']):
        missing_items.append("Bottom")
    if not any(type in current_types for type in outfit_rules['shoes']):
        missing_items.append("Shoes")
    
    # Suggest accessories if none present
    if not any(type in current_types for type in outfit_rules['accessories']):
        missing_items.append("Accessories")
    
    # Suggest outerwear based on season
    if not any(type in current_types for type in outfit_rules['outerwear']):
        missing_items.append("Outerwear")
    
    return missing_items

def get_shopping_recommendations(search_query, style_context=""):
    """Get shopping recommendations using SERP API"""
    try:
        # Get API key from Streamlit secrets
        api_key = st.secrets["SERPAPI_KEY"]
        
        # Set up the parameters for the API call
        params = {
            "api_key": api_key,
            "engine": "google_shopping",
            "q": search_query,
            "num": 6,
            "price_low": 0,
            "price_high": 1000,
            "gl": "us"
        }

        # Make the API request
        response = requests.get("https://serpapi.com/search", params=params)
        data = response.json()

        if "shopping_results" in data:
            results = data["shopping_results"]
            return results
        else:
            st.warning("No shopping results found.")
            return None
            
    except KeyError:
        st.error("SERP API key not found. Please check your secrets.toml file.")
        return None
    except Exception as e:
        st.error(f"Error fetching shopping recommendations: {str(e)}")
        return None

def display_shopping_recommendations(recommendations, section_id=""):
    """Display shopping recommendations in a grid layout"""
    if not recommendations:
        return

    # Create rows of 3 items each
    for i in range(0, len(recommendations), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(recommendations):
                item = recommendations[i + j]
                with col:
                    # Get the correct product link
                    product_link = item.get('product_link', '')  # Direct Google Shopping link
                    
                    # Display product image
                    if 'thumbnail' in item:
                        st.image(item['thumbnail'], use_column_width=True)
                    
                    # Display link immediately under the image
                    if product_link:
                        st.markdown(f'<a href="{product_link}" target="_blank" style="display: block; text-align: center; margin: 5px 0;">🛍️ Shop Now</a>', unsafe_allow_html=True)
                    
                    # Display other product details
                    title = item.get('title', 'No title')[:50]
                    price = item.get('price', 'Price not available')
                    source = item.get('source', '')
                    
                    st.markdown(f"""
                        **{title}...**  
                        💰 {price}  
                        🏪 {source}
                    """)




=======
>>>>>>> 82784ae66500dcd327bb26ca80802df0894371fb

if __name__ == "__main__":
    main()