import streamlit as st
import pandas as pd
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





if __name__ == "__main__":
   main()