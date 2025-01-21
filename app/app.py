import streamlit as st
from pydantic import BaseModel
from dotenv import load_dotenv
import openai
import os
from PIL import Image
import pandas as pd
import hashlib
import uuid
import json
from datetime import datetime, timedelta
import time
import requests
import re
import numpy as np
import cv2
from streamlit_drawable_canvas import st_canvas
import io
try:
    import pyperclip
except ImportError:
    # Fallback if pyperclip is not available
    class PyperclipFallback:
        def copy(self, text):
            st.code(text, language=None)
    pyperclip = PyperclipFallback()

## clare's comments
#minoo

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)
USER_DB_PATH = "user_db.csv"




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
class ClothingItemResponse(BaseModel):
   name: str
   color: str
   type_of_clothing: str
   season: str
   occasion: str
   additional_details: str = ""  # New field for additional details




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


   response = client.chat.completions.create(
       model="gpt-4",
       messages=[
           {"role": "system", "content": prompt},
           {"role": "user", "content": item_description}
       ]
   )
  
   try:
       import json
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




# Clothing management functions
def load_user_clothing():
   user_file = f"{st.session_state.username}_clothing.csv"
   if os.path.exists(user_file):
       return pd.read_csv(user_file)
   else:
       return pd.DataFrame(columns=["id", "name", "color", "type_of_clothing", "season", "occasion", "image_path"])




def save_user_clothing(df):
   """Save the user's clothing data to a CSV file"""
   user_file = f"{st.session_state.username}_clothing.csv"
   df.to_csv(user_file, index=False)




def check_duplicate_name(name: str, user_clothing: pd.DataFrame) -> bool:
   """Check if a name already exists in the user's clothing database"""
   return name.lower() in user_clothing['name'].str.lower().values




def suggest_unique_name(base_name: str, user_clothing: pd.DataFrame) -> str:
   """Generate a unique name by adding a number if the base name exists"""
   if not check_duplicate_name(base_name, user_clothing):
       return base_name
  
   counter = 1
   while True:
       new_name = f"{base_name} ({counter})"
       if not check_duplicate_name(new_name, user_clothing):
           return new_name
       counter += 1




def image_uploader_and_display():
   st.title("Add to Your Wardrobe")
  
   save_directory = "uploads"
   if not os.path.exists(save_directory):
       try:
           os.makedirs(save_directory)
       except Exception as e:
           st.error(f"Could not create uploads directory: {e}")
           return


   uploaded_files = st.file_uploader("Choose an image file", accept_multiple_files=True, type=["jpg", "jpeg", "png", "webp"])


   if uploaded_files:
       st.markdown("<h3 style='color: #2c3e50;'>New Items</h3>", unsafe_allow_html=True)
      
       # Load existing clothing data once
       user_clothing = load_user_clothing()
      
       for uploaded_file in uploaded_files:
           try:
               image = Image.open(uploaded_file)
               st.image(image, caption=uploaded_file.name, width=150)


               image_path = os.path.join(save_directory, uploaded_file.name)
               image.save(image_path)


               description = f"""Please analyze this clothing item in detail: {uploaded_file.name}.
               Consider its style, design, and any distinctive features to create a unique and descriptive name."""
              
               clothing_description = gpt4o_structured_clothing(description)
              
               # Generate a unique name based on AI suggestion
               suggested_name = suggest_unique_name(clothing_description.name, user_clothing)


               with st.container():
                   st.markdown("<div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
                  
                   # Display AI-generated name with option to edit
                   st.markdown(f"""
                       <div style='margin-bottom: 15px;'>
                           <strong>AI-Suggested Name:</strong> {suggested_name}
                       </div>
                   """, unsafe_allow_html=True)
                  
                   name = st.text_input(
                       "Item Name (Edit if needed)",
                       value=suggested_name,
                       help="You can keep the AI-suggested name or create your own. Names must be unique.",
                       key=f"name_input_{uploaded_file.name}"
                   )


                   # Color selection with predefined options
                   color_options = ["Red", "Blue", "Green", "Yellow", "Black", "White", "Purple", "Orange", "Pink", "Brown", "Gray", "Multi-color"]
                   colors = st.multiselect(
                       "Colors",
                       options=color_options,
                       default=[clothing_description.color] if clothing_description.color in color_options else [],
                       key=f"colors_multiselect_{uploaded_file.name}"
                   )


                   # Type of clothing with predefined options
                   type_options = ["Shirt", "Pants", "Jacket", "Dress", "Skirt", "Shorts", "Sweater", "T-shirt", "Blouse", "Coat", "Jeans", "Shoes"]
                   type_of_clothing = st.selectbox(
                       "Type of Clothing",
                       options=type_options,
                       index=type_options.index(clothing_description.type_of_clothing) if clothing_description.type_of_clothing in type_options else 0,
                       key=f"type_selectbox_{uploaded_file.name}"
                   )


                   # Season selection with detailed descriptions
                   season_options = {
                       "Spring": "Light to medium weight, transitional pieces",
                       "Summer": "Lightweight, breathable materials",
                       "Fall": "Medium weight, layering pieces",
                       "Winter": "Heavy, warm materials",
                       "All Seasons": "Versatile pieces suitable year-round"
                   }
                   seasons = st.multiselect(
                       "Suitable Seasons",
                       options=list(season_options.keys()),
                       default=[clothing_description.season] if clothing_description.season in season_options.keys() else [],
                       help="Select all applicable seasons for this item",
                       key=f"seasons_multiselect_{uploaded_file.name}"
                   )


                   # Occasion selection with detailed descriptions
                   occasion_options = {
                       "Casual": "Everyday, relaxed settings",
                       "Formal": "Special events, ceremonies",
                       "Business": "Office, professional settings",
                       "Party": "Social gatherings, celebrations",
                       "Sports": "Athletic activities",
                       "Outdoor": "Nature activities, hiking",
                       "Beach": "Seaside, summer activities",
                       "Wedding": "Wedding ceremonies and receptions",
                       "Everyday": "Regular daily activities"
                   }
                   occasions = st.multiselect(
                       "Appropriate Occasions",
                       options=list(occasion_options.keys()),
                       default=[clothing_description.occasion] if clothing_description.occasion in occasion_options.keys() else [],
                       help="Select all occasions where this item would be appropriate",
                       key=f"occasions_multiselect_{uploaded_file.name}"
                   )


                   # Add new field for additional details
                   additional_details = st.text_area(
                       "Additional Details",
                       value=clothing_description.additional_details,
                       help="Enter any distinctive features, patterns, prints, logos, materials, or special care instructions",
                       key=f"additional_details_{uploaded_file.name}"
                   )


                   if st.button("Save", key=f"save_button_{uploaded_file.name}"):
                       # Check if the user-edited name is unique
                       if check_duplicate_name(name, user_clothing):
                           st.error(f"An item with the name '{name}' already exists. Please choose a different name.")
                           continue
                      
                       new_data = pd.DataFrame([{
                           "id": str(uuid.uuid4()),
                           "name": name,
                           "image_path": image_path,
                           "color": ", ".join(colors),
                           "type_of_clothing": type_of_clothing,
                           "season": ", ".join(seasons),
                           "occasion": ", ".join(occasions),
                           "additional_details": additional_details
                       }])
                      
                       # Update the user_clothing DataFrame
                       user_clothing = pd.concat([user_clothing, new_data], ignore_index=True)
                       save_user_clothing(user_clothing)
                       st.success(f"'{name}' saved successfully!")


                   st.markdown("</div>", unsafe_allow_html=True)


           except Exception as e:
               st.error(f"Error processing {uploaded_file.name}: {str(e)}")
               continue




def display_saved_clothes():
   st.title("👚 Saved Clothes")


   user_clothing = load_user_clothing()


   if user_clothing.empty:
       st.write("No clothes saved yet!")
       return


   clothing_type_options = ["Shirt", "Pants", "Jacket", "Dress", "Skirt", "Shorts", "Sweater", "T-shirt", "Blouse", "Coat", "Jeans", "Shoes"]
   selected_clothing_types = st.multiselect("Select Clothing Types to Filter", clothing_type_options)


   color_options = ["Red", "Blue", "Green", "Yellow", "Black", "White", "Purple", "Orange", "Pink", "Brown", "Gray", "Multi-color"]
   selected_colors = st.multiselect("Select Colors to Filter", color_options)


   season_options = ["Spring", "Summer", "Fall", "Winter", "All Seasons"]
   selected_seasons = st.multiselect("Select Seasons to Filter", season_options)


   occasion_options = ["Casual", "Formal", "Business", "Party", "Sports", "Outdoor", "Beach", "Wedding", "Everyday"]
   selected_occasions = st.multiselect("Select Occasions to Filter", occasion_options)


   if st.button("Filter Clothes"):
       if not user_clothing.empty:
           filtered_clothes = user_clothing


           if selected_clothing_types:
               filtered_clothes = filtered_clothes[filtered_clothes['type_of_clothing'].isin(selected_clothing_types)]
           if selected_colors:
               filtered_clothes = filtered_clothes[filtered_clothes['color'].isin(selected_colors)]
           if selected_seasons:
               filtered_clothes = filtered_clothes[filtered_clothes['season'].isin(selected_seasons)]
           if selected_occasions:
               filtered_clothes = filtered_clothes[filtered_clothes['occasion'].isin(selected_occasions)]


           clothes_per_row = 3
           for i in range(0, len(filtered_clothes), clothes_per_row):
               cols = st.columns(clothes_per_row)
               for idx, item in enumerate(filtered_clothes.iloc[i:i + clothes_per_row].to_dict(orient='records')):
                   with cols[idx]:
                       try:
                           image_path = item['image_path']
                           if not os.path.exists(image_path):
                               new_path = os.path.join('uploads', os.path.basename(image_path))
                               if os.path.exists(new_path):
                                   image_path = new_path
                                   user_clothing.loc[user_clothing['id'] == item['id'], 'image_path'] = new_path
                                   save_user_clothing(user_clothing)
                          
                           if os.path.exists(image_path):
                               with open(image_path, 'rb') as file:
                                   image_bytes = file.read()
                               st.image(image_bytes, caption=item['name'], width=150)
                           else:
                               st.warning(f"Image not found for {item['name']}")
                          
                           st.write(f"**Colors**: {item['color']}")
                           st.write(f"**Type of Clothing**: {item['type_of_clothing']}")
                           st.write(f"**Seasons**: {item['season']}")
                           st.write(f"**Occasions**: {item['occasion']}")
                          
                           if item.get('additional_details'):  # Only show if details exist
                               st.markdown(f"""
                                   <div style='margin-top: 10px; padding: 10px; border-left: 3px solid #2c3e50;'>
                                       <strong>Details:</strong><br>
                                       {item['additional_details']}
                                   </div>
                               """, unsafe_allow_html=True)
                          
                           unique_key = f"delete_{item['id']}"
                           if st.button(f"Delete {item['name']}", key=unique_key):
                               if os.path.exists(image_path):
                                   try:
                                       os.remove(image_path)
                                   except Exception as e:
                                       st.warning(f"Could not delete image file: {e}")
                              
                               user_clothing = user_clothing[user_clothing['id'] != item['id']]
                               save_user_clothing(user_clothing)
                               st.success(f"{item['name']} deleted successfully.")
                               st.rerun()
                           st.write("---")
                       except Exception as e:
                           st.error(f"Error displaying {item['name']}: {str(e)}")
                           continue


           if filtered_clothes.empty:
               st.write("No matching clothes found.")
       else:
           st.write("No clothes saved yet.")




def logout():
   if st.sidebar.button("Logout"):
       st.session_state.clear()
       st.rerun()




def load_saved_outfits():
   """Load saved outfits from JSON file"""
   outfit_file = f"{st.session_state.username}_outfits.json"
   try:
       if os.path.exists(outfit_file):
           with open(outfit_file, 'r') as f:
               outfits = json.load(f)
               st.write(f"Debug: Loaded {len(outfits)} outfits")
               return outfits
       st.write("Debug: No outfits file found")
       return []
   except Exception as e:
       st.error(f"Error loading outfits: {str(e)}")
       return []




def save_outfit(outfit_items, outfit_name, occasion):
    """
    Save an outfit with its items, name, and occasion.
    Returns True if successful, False otherwise.
    """
    try:
        # Create the outfit file path
        outfit_file = f"{st.session_state.username}_outfits.json"
        
        # Basic validation
        if not outfit_items or not outfit_name or not occasion:
            st.error("Missing required outfit information")
            return False

        # Create new outfit object
        new_outfit = {
            "id": str(uuid.uuid4()),
            "name": outfit_name.strip(),
            "items": outfit_items,  # Keep the original item dictionaries
            "occasion": occasion,
            "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Load existing outfits or create new list
        outfits = []
        if os.path.exists(outfit_file):
            try:
                with open(outfit_file, 'r') as f:
                    outfits = json.load(f)
            except:
                outfits = []

        # Add new outfit
        outfits.append(new_outfit)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(outfit_file) if os.path.dirname(outfit_file) else '.', exist_ok=True)

        # Save to file
        with open(outfit_file, 'w') as f:
            json.dump(outfits, f, indent=2)
            
        # Print debug information
        st.write(f"Debug: Saved outfit '{outfit_name}' with {len(outfit_items)} items")
        st.write(f"Debug: File location: {os.path.abspath(outfit_file)}")
        
        return True

    except Exception as e:
        st.error(f"Failed to save outfit: {str(e)}")
        import traceback
        st.write("Debug: Full error trace:", traceback.format_exc())
        return False




def clothing_data_insights():
    st.title("Clothing Data Insights with GPT-4")
    user_clothing = load_user_clothing()

    if user_clothing.empty:
        st.info("Add some clothes to your wardrobe first!")
        return

    user_question = st.text_input(
        "Ask about outfit combinations or styling advice:",
        placeholder="Example: What should I wear for a casual summer day?"
    )

    if st.button("Get Insights"):
        if user_question.strip() == "":
            st.error("Please enter a question.")
        else:
            prompt = f"""Based on this wardrobe data:
            {user_clothing[['name', 'type_of_clothing', 'color', 'occasion', 'season']].to_string()}
            
            Answer the following question by ONLY listing the specific names of items from the wardrobe above.
            Do not add any descriptions or explanations. Just list the item names, one per line.
            
            Question: {user_question}"""

            with st.spinner("Generating outfit suggestions..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a fashion expert. Respond only with the exact names of clothing items from the provided wardrobe, one item per line."},
                        {"role": "user", "content": prompt}
                    ]
                )

                suggested_items = response.choices[0].message.content.strip().split('\n')
                
                st.markdown("### 👗 Suggested Outfit")
                
                cols = st.columns(3)
                valid_items = []
                
                for idx, item_name in enumerate(suggested_items):
                    item_name = item_name.strip('- ').strip()
                    matching_item = user_clothing[user_clothing['name'].str.lower() == item_name.lower()]
                    
                    if not matching_item.empty:
                        with cols[idx % 3]:
                            try:
                                image_path = matching_item.iloc[0]['image_path']
                                if os.path.exists(image_path):
                                    image = Image.open(image_path)
                                    st.image(image, caption=item_name, use_column_width=True)
                                    valid_items.append({
                                        "name": item_name,
                                        "image_path": image_path,
                                        "type_of_clothing": matching_item.iloc[0]['type_of_clothing'],
                                        "color": matching_item.iloc[0]['color']
                                    })
                                else:
                                    st.warning(f"Image not found for: {item_name}")
                            except Exception as e:
                                st.error(f"Error displaying image for: {item_name}")

                if valid_items:
                    st.markdown("### 💾 Save This Outfit")
                    
                    outfit_name = st.text_input(
                        "Outfit Name",
                        value=f"Outfit {datetime.now().strftime('%Y%m%d_%H%M')}",
                        key="gpt_outfit_name"
                    )
                    
                    occasion = st.selectbox(
                        "When would you wear this outfit?",
                        options=[
                            "Casual", "Formal", "Business", "Business Casual",
                            "Party", "Date Night", "Weekend", "Vacation",
                            "Outdoor Activities", "Special Event", "Wedding",
                            "Interview", "Dinner", "Other"
                        ],
                        key="gpt_occasion"
                    )
                    
                    # Preview items
                    st.markdown("#### Items in this outfit:")
                    for item in valid_items:
                        st.write(f"- {item['name']} ({item['type_of_clothing']})")
                    
                    # Save button
                    if st.button("💾 Save Outfit", key="save_gpt_outfit", type="primary"):
                        try:
                            st.write("Debug: Save button clicked")
                            st.write(f"Debug: Outfit name: {outfit_name}")
                            st.write(f"Debug: Number of items: {len(valid_items)}")
                            
                            if not outfit_name:
                                st.error("Please provide an outfit name")
                            else:
                                success = save_outfit(valid_items, outfit_name, occasion)
                                if success:
                                    st.success(f"✨ Outfit '{outfit_name}' saved successfully!")
                                    # Give user time to see the success message
                                    time.sleep(2)
                                    # Force a page refresh
                                    st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error saving outfit: {str(e)}")
                            st.write("Debug: Save button error:", str(e))




def display_saved_outfits():
   """
   Display all saved outfits in a grid layout with images and details
   """
   st.title("📱 Saved Outfits")
  
   outfit_file = f"{st.session_state.username}_outfits.json"
  
   # Load user's clothing items
   user_clothing = load_user_clothing()
  
   if user_clothing.empty:
       st.info("Add some clothes to your wardrobe first!")
       return
  
   # Add "Create New Outfit" button at the top
   if st.button("➕ Create New Outfit", type="primary"):
       st.session_state.creating_outfit = True
  
   # Manual outfit creation interface
   if 'creating_outfit' in st.session_state and st.session_state.creating_outfit:
       st.markdown("### Create New Outfit")
      
       col1, col2 = st.columns(2)
       with col1:
           # Outfit name input
           outfit_name = st.text_input(
               "Outfit Name",
               value=f"Outfit {datetime.now().strftime('%Y%m%d_%H%M')}",
               key="manual_outfit_name"
           )
      
       with col2:
           # Enhanced occasion selection with more options and descriptions
           occasion = st.selectbox(
               "When would you wear this outfit?",
               options=[
                   "Casual",
                   "Formal",
                   "Business",
                   "Business Casual",
                   "Party",
                   "Date Night",
                   "Weekend",
                   "Vacation",
                   "Outdoor Activities",
                   "Workout",
                   "Special Event",
                   "Wedding",
                   "Interview",
                   "Dinner",
                   "Beach",
                   "Other"
               ],
               help="Select the occasion or setting where you'd wear this outfit",
               key="manual_occasion"
           )
      
       # Add occasion description
       occasion_descriptions = {
           "Casual": "Everyday, relaxed settings",
           "Formal": "Upscale events and formal gatherings",
           "Business": "Professional office environment",
           "Business Casual": "Relaxed office or professional settings",
           "Party": "Social gatherings and celebrations",
           "Date Night": "Romantic evenings out",
           "Weekend": "Relaxed weekend activities",
           "Vacation": "Travel and leisure",
           "Outdoor Activities": "Nature, hiking, or outdoor events",
           "Workout": "Exercise and athletic activities",
           "Special Event": "Important occasions and celebrations",
           "Wedding": "Wedding ceremonies and receptions",
           "Interview": "Job interviews and professional meetings",
           "Dinner": "Restaurant dining and dinner events",
           "Beach": "Beach and poolside activities",
           "Other": "Custom occasion"
       }
      
       st.markdown(f"*{occasion_descriptions.get(occasion, '')}*")
      
       if occasion == "Other":
           custom_occasion = st.text_input("Specify the occasion:", key="custom_occasion")
           occasion = custom_occasion if custom_occasion else occasion
      
       # Group clothing items by type for easier selection
       clothing_by_type = {}
       for _, item in user_clothing.iterrows():
           type_of_clothing = item['type_of_clothing']
           if type_of_clothing not in clothing_by_type:
               clothing_by_type[type_of_clothing] = []
           clothing_by_type[type_of_clothing].append({
               'name': item['name'],
               'image_path': item['image_path'],
               'type_of_clothing': item['type_of_clothing'],
               'color': item['color']
           })
      
       # Create expandable sections for each clothing type
       selected_items = []
       for clothing_type, items in clothing_by_type.items():
           with st.expander(f"Select {clothing_type}"):
               cols = st.columns(3)
               for idx, item in enumerate(items):
                   with cols[idx % 3]:
                       if os.path.exists(item['image_path']):
                           image = Image.open(item['image_path'])
                           st.image(image, caption=item['name'], width=120)
                           if st.checkbox(f"Select {item['name']}", key=f"select_{item['name']}"):
                               selected_items.append(item)
      
       # Preview selected items
       if selected_items:
           st.markdown("### Selected Items")
           preview_cols = st.columns(min(len(selected_items), 3))
           for idx, item in enumerate(selected_items):
               with preview_cols[idx % 3]:
                   if os.path.exists(item['image_path']):
                       image = Image.open(item['image_path'])
                       st.image(image, caption=f"{item['name']} ({item['type_of_clothing']})", width=120)
      
       col1, col2 = st.columns(2)
       with col1:
           if st.button("Save Outfit", disabled=len(selected_items) == 0):
               if not outfit_name:
                   st.error("Please provide an outfit name")
               else:
                   if save_outfit(selected_items, outfit_name, occasion):
                       st.success(f"✨ Outfit '{outfit_name}' saved successfully!")
                       st.session_state.creating_outfit = False
                       time.sleep(1)
                       st.rerun()
                   else:
                       st.error("Failed to save outfit. Please try again.")
      
       with col2:
           if st.button("Cancel"):
               st.session_state.creating_outfit = False
               st.rerun()
  
   # Display existing outfits (only if not creating a new outfit)
   if not ('creating_outfit' in st.session_state and st.session_state.creating_outfit):
       if not os.path.exists(outfit_file):
           st.info("No outfits saved yet!")
           return
          
       try:
           with open(outfit_file, 'r') as f:
               saved_outfits = json.load(f)
              
           if not saved_outfits:
               st.info("No outfits saved yet!")
               return


           # Add filtering options
           st.markdown("### Filter Outfits")
           col1, col2 = st.columns(2)
          
           with col1:
               occasions = sorted(list(set(outfit['occasion'] for outfit in saved_outfits)))
               selected_occasions = st.multiselect(
                   "Filter by Occasion",
                   options=occasions,
                   help="Select one or more occasions to filter outfits"
               )


           with col2:
               date_range = st.date_input(
                   "Filter by Date Range",
                   value=(
                       datetime.strptime(min(outfit['date_created'] for outfit in saved_outfits), "%Y-%m-%d %H:%M:%S").date(),
                       datetime.strptime(max(outfit['date_created'] for outfit in saved_outfits), "%Y-%m-%d %H:%M:%S").date()
                   ),
                   help="Select a date range to filter outfits"
               )


           # Filter outfits based on selected criteria
           filtered_outfits = saved_outfits
          
           if selected_occasions:
               filtered_outfits = [
                   outfit for outfit in filtered_outfits
                   if outfit['occasion'] in selected_occasions
               ]


           if len(date_range) == 2:
               start_date, end_date = date_range
               filtered_outfits = [
                   outfit for outfit in filtered_outfits
                   if start_date <= datetime.strptime(outfit['date_created'], "%Y-%m-%d %H:%M:%S").date() <= end_date
               ]


           # Display number of filtered results
           st.markdown(f"### Showing {len(filtered_outfits)} outfit{'s' if len(filtered_outfits) != 1 else ''}")
              
           # Display filtered outfits in grid
           for i in range(0, len(filtered_outfits), 2):
               cols = st.columns(2)
               for j in range(2):
                   if i + j < len(filtered_outfits):
                       outfit = filtered_outfits[i + j]
                       with cols[j]:
                           st.markdown(f"""
                               <div style='
                                   background-color: white;
                                   padding: 1.5rem;
                                   border-radius: 10px;
                                   box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                                   margin-bottom: 1.5rem;
                               '>
                                   <h3 style='margin-bottom: 0.5rem;'>{outfit['name']}</h3>
                                   <p style='color: #666;'><strong>Occasion:</strong> {outfit['occasion']}</p>
                                   <p style='color: #888; font-size: 0.9em;'>Created: {outfit['date_created']}</p>
                               </div>
                           """, unsafe_allow_html=True)
                          
                           # Display outfit items
                           for item in outfit['items']:
                               if os.path.exists(item['image_path']):
                                   image = Image.open(item['image_path'])
                                   caption = item['name']
                                   if 'type_of_clothing' in item:
                                       caption = f"{item['name']} ({item['type_of_clothing']})"
                                   st.image(image, caption=caption, width=120)
                               else:
                                   st.warning(f"Image not found for: {item['name']}")
                          
                           if st.button(f"Delete Outfit", key=f"delete_{outfit['id']}"):
                               saved_outfits.remove(outfit)
                               with open(outfit_file, 'w') as f:
                                   json.dump(saved_outfits, f, indent=2)
                               st.success("Outfit deleted successfully!")
                               time.sleep(0.5)
                               st.rerun()
                              
       except Exception as e:
           st.error(f"Error loading outfits: {str(e)}")
           # Add debug information
           st.write("Debug: Outfit file contents:")
           try:
               with open(outfit_file, 'r') as f:
                   st.write(json.load(f))
           except Exception as debug_e:
               st.write(f"Debug: Could not read outfit file: {str(debug_e)}")




def migrate_images():
   # Only run migration if user is logged in
   if "username" in st.session_state and st.session_state.username:
       if not os.path.exists('uploads'):
           os.makedirs('uploads')
          
       user_clothing = load_user_clothing()
       if not user_clothing.empty:
           for idx, row in user_clothing.iterrows():
               old_path = row['image_path']
               if old_path.startswith('/Users') and os.path.exists(old_path):
                   try:
                       new_path = os.path.join('uploads', os.path.basename(old_path))
                       with open(old_path, 'rb') as src, open(new_path, 'wb') as dst:
                           dst.write(src.read())
                       user_clothing.loc[idx, 'image_path'] = new_path
                   except Exception as e:
                       print(f"Error migrating {old_path}: {e}")
           save_user_clothing(user_clothing)




def update_image_paths():
   user_clothing = load_user_clothing()
   if not user_clothing.empty:
       for idx, row in user_clothing.iterrows():
           old_path = row['image_path']
           if not os.path.exists(old_path):
               new_path = os.path.join('uploads', os.path.basename(old_path))
               if os.path.exists(new_path):
                   user_clothing.loc[idx, 'image_path'] = new_path
       save_user_clothing(user_clothing)




def show_tutorial():
    """Display a comprehensive guide for new users"""
    st.title("🎯 Getting Started with Your Digital Wardrobe")
    
    # Welcome Section
    st.markdown("""
        ### Welcome to Your Digital Wardrobe! 
        Let's walk through how to make the most of your new digital closet.
    """)
    
    # Navigation Guide
    st.markdown("""
        ### 📍 Navigation
        You'll find four main sections in the sidebar:
        1. **Image Uploader and Display** - Add clothes to your wardrobe
        2. **Saved Clothes** - View and manage your clothing items
        3. **Clothing Data Insights** - Get AI-powered outfit suggestions
        4. **Saved Outfits** - Create and view your outfit combinations
    """)
    
    # Adding Clothes Tutorial
    with st.expander("📸 How to Add Clothes", expanded=True):
        st.markdown("""
            1. Go to **Image Uploader and Display**
            2. Click 'Browse files' to upload photos of your clothes
            3. For each item:
                - Verify or edit the AI-suggested name
                - Select colors, type, seasons, and occasions
                - Add any additional details
                - Click 'Save' to add to your wardrobe
            
            **Pro tip**: Take photos of your clothes on a clear background for best results!
        """)
    
    # Managing Clothes Tutorial
    with st.expander("👕 Managing Your Wardrobe", expanded=True):
        st.markdown("""
            In the **Saved Clothes** section:
            - View all your uploaded items
            - Filter by type, color, season, or occasion
            - Delete items you no longer want
            - View detailed information about each piece
        """)
    
    # Getting Outfit Suggestions
    with st.expander("🤖 Getting AI Outfit Suggestions", expanded=True):
        st.markdown("""
            In **Clothing Data Insights**:
            1. Ask any question about outfit combinations
                - "What should I wear to a summer wedding?"
                - "Create a casual outfit for cold weather"
                - "Suggest a professional look for a meeting"
            2. GPT-4 will suggest outfits using your actual clothes
            3. Save combinations you like to your Saved Outfits
        """)
    
    # Creating Outfits Tutorial
    with st.expander("👗 Creating and Managing Outfits", expanded=True):
        st.markdown("""
            In **Saved Outfits**:
            1. Create outfits manually or save AI suggestions
            2. Name your outfits and specify occasions
            3. View all saved outfits in a grid
            4. Filter outfits by occasion or date
            5. Delete outfits you no longer want
            
            **Pro tip**: Create outfits for different occasions to make daily dressing easier!
        """)
    
    # Style Profile Info
    st.markdown(f"""
        ### 🎨 Your Style Profile
        Based on your quiz results, your style aesthetic is: **{st.session_state.get('style_aesthetic', 'Not set')}**
        
        We'll use this to help create outfits that match your personal style!
    """)
    
    # Ready to Start
    st.markdown("---")
    if st.button("I'm Ready to Start!", type="primary"):
        st.session_state.show_tutorial = False
        st.rerun()

def style_quiz():
    """
    Quiz to determine user's style aesthetic.
    Returns True when completed.
    """
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

    if not st.session_state.quiz_completed:
        st.title("🎨 Discover Your Style")
        if st.session_state.get('retaking_quiz', False):
            st.markdown("""
                ### Retaking the Style Quiz
                Let's update your style profile! Answer these questions based on your current preferences.
            """)
        else:
            st.markdown("Let's find out your personal style aesthetic! Answer these questions to help us understand your fashion preferences.")

        # Initialize session state for responses if not exists
        if 'quiz_responses' not in st.session_state:
            st.session_state.quiz_responses = {}

        # Quiz questions
        questions = {
            'color_palette': {
                'question': "Which color palette resonates with you the most?",
                'options': [
                    "Neutrals (Black, White, Beige, Gray)",
                    "Pastels (Soft Pink, Light Blue, Mint)",
                    "Bold & Bright (Red, Yellow, Electric Blue)",
                    "Earth Tones (Brown, Olive, Rust)",
                    "Monochrome (Black & White)",
                    "Jewel Tones (Deep Purple, Emerald, Ruby)"
                ]
            },
            'style_icons': {
                'question': "Which style icon's aesthetic do you most admire?",
                'options': [
                    "Audrey Hepburn (Classic Elegance)",
                    "Kate Moss (Effortless Cool)",
                    "Rihanna (Bold and Experimental)",
                    "Steve Jobs (Minimal Tech)",
                    "Harry Styles (Gender-Fluid, Eclectic)",
                    "Zendaya (Modern Sophistication)"
                ]
            },
            'weekend_outfit': {
                'question': "What's your go-to weekend outfit?",
                'options': [
                    "Athleisure (Leggings, Sneakers, Comfortable Tops)",
                    "Casual Chic (Jeans, Blouse, Accessories)",
                    "Bohemian (Flowy Dresses, Natural Fabrics)",
                    "Edgy (Leather Jacket, Boots, Dark Colors)",
                    "Preppy (Tailored Pieces, Classic Patterns)",
                    "Streetwear (Oversized, Modern, Bold)"
                ]
            }
        }

        # Display questions
        for key, data in questions.items():
            st.session_state.quiz_responses[key] = st.radio(
                data['question'],
                data['options'],
                key=f"quiz_{key}"
            )
            st.markdown("---")

        if st.button("✨ Discover My Style", type="primary"):
            # Analyze responses
            style = analyze_style_preferences(st.session_state.quiz_responses)
            
            # Save style to user profile
            save_user_style(st.session_state.username, style)
            st.session_state.style_aesthetic = style
            st.session_state.quiz_completed = True
            st.rerun()

    else:  # Show results and transition to tutorial
        st.success("🎉 Style Analysis Complete!")
        st.markdown(f"""
            ## Your Style Aesthetic: {st.session_state.style_aesthetic}
            
            We'll use this information to help create outfits that match your personal style!
            
            Click continue to learn how to use Your Digital Wardrobe.
        """)
        
        if st.button("Continue to Tutorial", type="primary"):
            st.session_state.show_style_quiz = False
            st.session_state.show_tutorial = True
            st.session_state.quiz_completed = False  # Reset for next time
            st.session_state.retaking_quiz = False  # Reset retaking flag
            st.rerun()

    return False

def analyze_style_preferences(responses):
    """Analyze quiz responses using GPT-4 to determine style aesthetic"""
    prompt = f"""Based on these style preferences:
    Color Preference: {responses['color_palette']}
    Style Icon: {responses['style_icons']} we
    Weekend Outfit: {responses['weekend_outfit']}
    
    Determine the user's primary style aesthetic from these options:
    - Minimalist
    - Classic
    - Bohemian
    - Streetwear
    - Preppy
    - Avant-garde
    - Romantic
    - Athletic
    - Vintage
    - Modern
    
    Return ONLY the style name, nothing else."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a fashion expert. Analyze the style preferences and return only one word representing the primary style aesthetic."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip()

def save_user_style(username, style_aesthetic):
    """Save user's style aesthetic to their profile"""
    try:
        profile_file = f"{username}_profile.json"
        profile_data = {
            "style_aesthetic": style_aesthetic,
            "quiz_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving style profile: {str(e)}")

def get_weather(city):
    """Get current weather data for a city"""
    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        st.error("Weather API key not found. Please check your .env file.")
        return None
        
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    try:
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        response = requests.get(base_url, params=params)
        weather_data = response.json()
        
        if response.status_code == 200:
            return {
                'temperature': round(weather_data['main']['temp']),
                'description': weather_data['weather'][0]['main'],
                'humidity': weather_data['main']['humidity'],
                'wind_speed': weather_data['wind']['speed']
            }
        else:
            st.error(f"Error getting weather: {weather_data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"Error accessing weather service: {str(e)}")
        return None

def suggest_weather_appropriate_outfit(weather_data, user_clothing, style_aesthetic):
    """Get GPT-4 to suggest an outfit based on weather and user's style"""
    
    prompt = f"""As a fashion expert, suggest an outfit from the user's wardrobe considering:

Current Weather:
- Temperature: {weather_data['temperature']}°C
- Conditions: {weather_data['description']}
- Humidity: {weather_data['humidity']}%
- Wind Speed: {weather_data['wind_speed']} m/s

User's Style: {style_aesthetic}

Available Clothing Items:
{user_clothing[['name', 'type_of_clothing', 'color', 'season']].to_string()}

Suggest an appropriate outfit by listing specific items from their wardrobe that would:
1. Be comfortable in the current weather
2. Match their style aesthetic
3. Be appropriate for the conditions

Return ONLY the names of the suggested items, one per line."""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a fashion expert who specializes in weather-appropriate outfit suggestions."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content.strip().split('\n')

def weather_based_outfits():
    """Interface for weather-based outfit suggestions"""
    st.title("🌤️ Weather-Based Outfit Suggestions")
    
    # Load user's style aesthetic
    profile_file = f"{st.session_state.username}_profile.json"
    style_aesthetic = "Classic"  # default
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
            style_aesthetic = profile_data.get('style_aesthetic', 'Classic')
    
    # Location input
    city = st.text_input("Enter your city:", placeholder="e.g., London, New York, Tokyo")
    
    if city:
        weather_data = get_weather(city)
        if weather_data:
            # Display weather information
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Temperature", f"{weather_data['temperature']}°C")
            with col2:
                st.metric("Conditions", weather_data['description'])
            with col3:
                st.metric("Humidity", f"{weather_data['humidity']}%")
            with col4:
                st.metric("Wind Speed", f"{weather_data['wind_speed']} m/s")
            
            # Load user's clothing
            user_clothing = load_user_clothing()
            
            if user_clothing.empty:
                st.info("Add some clothes to your wardrobe first!")
                return
            
            # Get outfit suggestion
            st.markdown("### 👔 Suggested Outfit")
            suggested_items = suggest_weather_appropriate_outfit(weather_data, user_clothing, style_aesthetic)
            
            # Display suggested outfit
            cols = st.columns(3)
            valid_items = []
            
            for idx, item_name in enumerate(suggested_items):
                item_name = item_name.strip('- ').strip()
                matching_item = user_clothing[user_clothing['name'].str.lower() == item_name.lower()]
                
                if not matching_item.empty:
                    with cols[idx % 3]:
                        try:
                            image_path = matching_item.iloc[0]['image_path']
                            if os.path.exists(image_path):
                                image = Image.open(image_path)
                                st.image(image, caption=item_name, use_column_width=True)
                                valid_items.append({
                                    "name": item_name,
                                    "image_path": image_path,
                                    "type_of_clothing": matching_item.iloc[0]['type_of_clothing'],
                                    "color": matching_item.iloc[0]['color']
                                })
                            else:
                                st.warning(f"Image not found for: {item_name}")
                        except Exception as e:
                            st.error(f"Error displaying image for: {item_name}")
            
            # Option to save the outfit
            if valid_items:
                st.markdown("### 💾 Save This Outfit")
                outfit_name = st.text_input(
                    "Outfit Name",
                    value=f"Weather Outfit {datetime.now().strftime('%Y%m%d_%H%M')}",
                    key="weather_outfit_name"
                )
                
                occasion = st.selectbox(
                    "When would you wear this outfit?",
                    options=[
                        "Casual", "Formal", "Business", "Business Casual",
                        "Party", "Date Night", "Weekend", "Vacation",
                        "Outdoor Activities", "Special Event", "Wedding",
                        "Interview", "Dinner", "Other"
                    ],
                    key="weather_occasion"
                )
                
                if st.button("💾 Save Outfit", key="save_weather_outfit"):
                    if save_outfit(valid_items, outfit_name, occasion):
                        st.success(f"✨ Outfit '{outfit_name}' saved successfully!")
                        time.sleep(1)
                        st.rerun()

def schedule_outfits():
    """Interface for scheduling outfits on a calendar"""
    st.title("📅 Outfit Calendar")
    
    # Load saved outfits
    outfits = load_saved_outfits()
    if not outfits:
        st.info("You don't have any saved outfits yet. Create some outfits first!")
        return
    
    # Calendar date selection
    selected_date = st.date_input(
        "Select a date to schedule an outfit",
        value=datetime.now().date()
    )
    
    # Load existing schedule
    schedule_file = f"{st.session_state.username}_schedule.json"
    schedule = load_outfit_schedule(schedule_file)
    
    # Display currently scheduled outfit for selected date
    date_str = selected_date.strftime("%Y-%m-%d")
    if date_str in schedule:
        st.markdown("### Currently Scheduled Outfit")
        scheduled_outfit = next((outfit for outfit in outfits if outfit['id'] == schedule[date_str]['outfit_id']), None)
        if scheduled_outfit:
            st.markdown(f"**{scheduled_outfit['name']}** ({schedule[date_str]['occasion']})")
            cols = st.columns(3)
            for idx, item in enumerate(scheduled_outfit['items']):
                with cols[idx % 3]:
                    if os.path.exists(item['image_path']):
                        image = Image.open(item['image_path'])
                        st.image(image, caption=item['name'], use_column_width=True)
    
    # Schedule new outfit
    st.markdown("### Schedule an Outfit")
    
    # Outfit selection
    outfit_names = [outfit['name'] for outfit in outfits]
    selected_outfit_name = st.selectbox(
        "Select an outfit",
        options=outfit_names,
        key=f"outfit_select_{date_str}"
    )
    
    selected_outfit = next((outfit for outfit in outfits if outfit['name'] == selected_outfit_name), None)
    
    if selected_outfit:
        # Preview selected outfit
        st.markdown("#### Preview:")
        cols = st.columns(3)
        for idx, item in enumerate(selected_outfit['items']):
            with cols[idx % 3]:
                if os.path.exists(item['image_path']):
                    image = Image.open(item['image_path'])
                    st.image(image, caption=item['name'], use_column_width=True)
        
        # Occasion selection
        occasion = st.selectbox(
            "Occasion",
            options=[
                "Work", "Casual", "Formal", "Business", "Date Night",
                "Weekend", "Special Event", "Other"
            ],
            key=f"occasion_select_{date_str}"
        )
        
        # Notes for this scheduled outfit
        notes = st.text_area(
            "Notes (optional)",
            placeholder="Add any notes about this outfit or occasion...",
            key=f"notes_{date_str}"
        )
        
        # Save button
        if st.button("Schedule Outfit", key=f"schedule_{date_str}"):
            schedule[date_str] = {
                'outfit_id': selected_outfit['id'],
                'occasion': occasion,
                'notes': notes
            }
            save_outfit_schedule(schedule_file, schedule)
            st.success(f"✨ Outfit scheduled for {selected_date.strftime('%B %d, %Y')}!")
            st.rerun()
    
    # Calendar view of scheduled outfits
    st.markdown("### 📅 Monthly Overview")
    month = selected_date.replace(day=1)
    month_calendar = create_month_calendar(month, schedule, outfits)
    st.markdown(month_calendar, unsafe_allow_html=True)

def load_outfit_schedule(schedule_file):
    """Load the outfit schedule from JSON file"""
    if os.path.exists(schedule_file):
        try:
            with open(schedule_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_outfit_schedule(schedule_file, schedule):
    """Save the outfit schedule to JSON file"""
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f, indent=2)

def create_month_calendar(month, schedule, outfits):
    """Create an HTML calendar showing scheduled outfits"""
    import calendar
    
    # Get the calendar for the month
    cal = calendar.monthcalendar(month.year, month.month)
    
    # Create HTML table
    html = f"""
    <div style="padding: 20px;">
        <h4 style="text-align: center;">{month.strftime('%B %Y')}</h4>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <th style="padding: 10px; text-align: center;">Mon</th>
                <th style="padding: 10px; text-align: center;">Tue</th>
                <th style="padding: 10px; text-align: center;">Wed</th>
                <th style="padding: 10px; text-align: center;">Thu</th>
                <th style="padding: 10px; text-align: center;">Fri</th>
                <th style="padding: 10px; text-align: center;">Sat</th>
                <th style="padding: 10px; text-align: center;">Sun</th>
            </tr>
    """
    
    for week in cal:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += '<td style="padding: 10px; border: 1px solid #ddd;"></td>'
            else:
                date_str = f"{month.year}-{month.month:02d}-{day:02d}"
                if date_str in schedule:
                    outfit = next((o for o in outfits if o['id'] == schedule[date_str]['outfit_id']), None)
                    outfit_name = outfit['name'] if outfit else "Unknown"
                    html += f"""
                        <td style="padding: 10px; border: 1px solid #ddd; background-color: #f0f8ff;">
                            <div style="font-weight: bold;">{day}</div>
                            <div style="font-size: 0.8em;">{outfit_name}</div>
                            <div style="font-size: 0.7em; color: #666;">{schedule[date_str]['occasion']}</div>
                        </td>
                    """
                else:
                    html += f'<td style="padding: 10px; border: 1px solid #ddd;">{day}</td>'
        html += "</tr>"
    
    html += "</table></div>"
    return html

def change_page(page_name: str):
    """Handle page navigation using JavaScript"""
    js = f"""
        <script>
            window.location.href = "?page={page_name}";
        </script>
    """
    st.markdown(js, unsafe_allow_html=True)

def homepage():
    """Display the homepage with outfit challenges and features"""
    st.title("🏠 Welcome to Your Digital Wardrobe")
    
    # User's Style Profile Summary
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"""
            ### 👋 Welcome back, {st.session_state.username}!
            
            Your Style: **{get_user_style()}**
        """)
    
    with col2:
        if st.button("📊 View My Stats", key="view_stats_button"):
            st.session_state.show_stats = not st.session_state.get('show_stats', False)
    
    with col3:
        if st.button("🎨 Retake Style Quiz"):
            st.session_state.show_style_quiz = True
            st.session_state.quiz_completed = False
    
    # Show stats if enabled
    if st.session_state.get('show_stats', False):
        show_wardrobe_stats()
        if st.button("Close Stats", key="close_stats_button"):
            st.session_state.show_stats = False
    
    # Outfit Challenges Section
    st.markdown("### 🏆 Outfit Challenges")
    
    if st.session_state.get('submitting_challenge', False):
        if submit_challenge_outfit():
            return
    
    # Weekly Challenge
    with st.expander("🌟 This Week's Challenge", expanded=True):
        current_challenge = get_current_challenge()
        st.markdown(f"""
            ### {current_challenge['title']}
            
            {current_challenge['description']}
            
            **Deadline**: {current_challenge['deadline']}
            **Participants**: {current_challenge['participants']} stylists
        """)
        
        if not check_challenge_participation(st.session_state.username, current_challenge['id']):
            if st.button("Join Challenge"):
                join_challenge(st.session_state.username, current_challenge['id'])
                st.success("You've joined the challenge! Start creating your outfit.")
        else:
            st.info("You're participating in this challenge!")
            if st.button("Submit Outfit"):
                st.session_state.submitting_challenge = True
                st.session_state.challenge_id = current_challenge['id']
                st.rerun()

    # Past Challenges
    with st.expander("🎨 Past Challenges"):
        show_past_challenges()

def get_user_style():
    """Get user's style from their profile"""
    profile_file = f"{st.session_state.username}_profile.json"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
            return profile_data.get('style_aesthetic', 'Not set')
    return "Not set"

def get_current_challenge():
    """Get the current weekly challenge"""
    challenges_file = "outfit_challenges.json"
    if not os.path.exists(challenges_file):
        # Create default challenge if none exists
        default_challenge = {
            "id": "challenge_001",
            "title": "Mix & Match Monochrome",
            "description": "Create a stunning outfit using only black and white pieces. Show us how you can make monochrome exciting!",
            "deadline": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "participants": 0,
            "status": "active"
        }
        save_challenges([default_challenge])
        return default_challenge
    
    with open(challenges_file, 'r') as f:
        challenges = json.load(f)
        return next((c for c in challenges if c['status'] == 'active'), challenges[0])

def check_challenge_participation(username, challenge_id):
    """Check if user is participating in a challenge"""
    participations_file = "challenge_participations.json"
    if os.path.exists(participations_file):
        with open(participations_file, 'r') as f:
            participations = json.load(f)
            return any(p['username'] == username and p['challenge_id'] == challenge_id 
                      for p in participations)
    return False

def join_challenge(username, challenge_id):
    """Add user to challenge participants"""
    participations_file = "challenge_participations.json"
    participations = []
    if os.path.exists(participations_file):
        with open(participations_file, 'r') as f:
            participations = json.load(f)
    
    participations.append({
        "username": username,
        "challenge_id": challenge_id,
        "joined_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "joined"
    })
    
    with open(participations_file, 'w') as f:
        json.dump(participations, f, indent=2)
    
    # Update challenge participants count
    challenges_file = "outfit_challenges.json"
    with open(challenges_file, 'r') as f:
        challenges = json.load(f)
    
    for challenge in challenges:
        if challenge['id'] == challenge_id:
            challenge['participants'] += 1
    
    with open(challenges_file, 'w') as f:
        json.dump(challenges, f, indent=2)

def show_past_challenges():
    """Display past challenges and winners"""
    challenges_file = "outfit_challenges.json"
    if os.path.exists(challenges_file):
        with open(challenges_file, 'r') as f:
            challenges = json.load(f)
            past_challenges = [c for c in challenges if c['status'] == 'completed']
            
            for challenge in past_challenges[:3]:  # Show last 3 challenges
                st.markdown(f"""
                    #### {challenge['title']}
                    *{challenge['description']}*
                    
                    Participants: {challenge['participants']}
                """)
                st.markdown("---")

def show_wardrobe_stats():
    """Display user's wardrobe statistics"""
    user_clothing = load_user_clothing()
    
    if not user_clothing.empty:
        st.markdown("### 📊 Your Wardrobe Stats")
        
        # Basic stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", len(user_clothing))
        with col2:
            st.metric("Types of Clothing", user_clothing['type_of_clothing'].nunique())
        with col3:
            st.metric("Color Palette", user_clothing['color'].nunique())
        
        # Clothing type distribution
        st.markdown("#### 👕 Clothing Types")
        type_counts = user_clothing['type_of_clothing'].value_counts()
        st.bar_chart(type_counts)
        
        # Color distribution
        st.markdown("#### 🎨 Color Distribution")
        color_counts = user_clothing['color'].str.split(', ').explode().value_counts()
        st.bar_chart(color_counts)
        
        # Season analysis
        st.markdown("#### 🌤️ Seasonal Distribution")
        season_counts = user_clothing['season'].str.split(', ').explode().value_counts()
        st.bar_chart(season_counts)
        
        # Occasion breakdown
        st.markdown("#### 🎭 Occasion Breakdown")
        occasion_counts = user_clothing['occasion'].str.split(', ').explode().value_counts()
        st.bar_chart(occasion_counts)
        
        # Recent additions
        st.markdown("#### 🆕 Recent Additions")
        recent_items = user_clothing.tail(5)
        for _, item in recent_items.iterrows():
            st.markdown(f"- {item['name']} ({item['type_of_clothing']})")
    else:
        st.info("Add some clothes to your wardrobe to see statistics!")

def save_challenges(challenges):
    """Save challenges to JSON file"""
    challenges_file = "outfit_challenges.json"
    with open(challenges_file, 'w') as f:
        json.dump(challenges, f, indent=2)

def submit_challenge_outfit():
    """Interface for submitting an outfit for a challenge"""
    st.markdown("### 🎯 Submit Your Challenge Outfit")
    
    # Load saved outfits
    outfits = load_saved_outfits()
    if not outfits:
        st.info("You need to create an outfit first! Go to Saved Outfits to create one.")
        return False
    
    # Outfit selection
    outfit_names = [outfit['name'] for outfit in outfits]
    selected_outfit_name = st.selectbox(
        "Select an outfit to submit",
        options=outfit_names
    )
    
    selected_outfit = next((outfit for outfit in outfits if outfit['name'] == selected_outfit_name), None)
    
    if selected_outfit:
        # Preview selected outfit
        st.markdown("#### Preview Your Submission:")
        cols = st.columns(3)
        for idx, item in enumerate(selected_outfit['items']):
            with cols[idx % 3]:
                if os.path.exists(item['image_path']):
                    image = Image.open(item['image_path'])
                    st.image(image, caption=item['name'], use_column_width=True)
        
        # Description
        description = st.text_area(
            "Tell us about your outfit (optional)",
            placeholder="Explain how your outfit meets the challenge..."
        )
        
        # Submit button
        if st.button("Submit Challenge Entry", type="primary"):
            success = save_challenge_submission(
                username=st.session_state.username,
                challenge_id=st.session_state.challenge_id,
                outfit_id=selected_outfit['id'],
                description=description
            )
            if success:
                st.success("🎉 Your outfit has been submitted to the challenge!")
                time.sleep(1)
                st.session_state.submitting_challenge = False
                st.rerun()
            else:
                st.error("Failed to submit outfit. Please try again.")
    
    if st.button("Cancel"):
        st.session_state.submitting_challenge = False
        st.rerun()
    
    return True

def save_challenge_submission(username, challenge_id, outfit_id, description=""):
    """Save a challenge submission"""
    try:
        submissions_file = "challenge_submissions.json"
        submissions = []
        if os.path.exists(submissions_file):
            with open(submissions_file, 'r') as f:
                submissions = json.load(f)
        
        # Create new submission
        submission = {
            "id": str(uuid.uuid4()),
            "username": username,
            "challenge_id": challenge_id,
            "outfit_id": outfit_id,
            "description": description,
            "submission_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "votes": 0
        }
        
        submissions.append(submission)
        
        # Save submissions
        with open(submissions_file, 'w') as f:
            json.dump(submissions, f, indent=2)
        
        # Update participation status
        update_participation_status(username, challenge_id, "submitted")
        
        return True
    except Exception as e:
        st.error(f"Error saving submission: {str(e)}")
        return False

def update_participation_status(username, challenge_id, status):
    """Update the status of a user's challenge participation"""
    participations_file = "challenge_participations.json"
    if os.path.exists(participations_file):
        with open(participations_file, 'r') as f:
            participations = json.load(f)
        
        for participation in participations:
            if (participation['username'] == username and 
                participation['challenge_id'] == challenge_id):
                participation['status'] = status
        
        with open(participations_file, 'w') as f:
            json.dump(participations, f, indent=2)

def style_quizzes():
    """Interactive quizzes for personal style education"""
    st.title("📚 Style Education & Quizzes")
    
    # Quiz Selection
    quiz_type = st.selectbox(
        "Choose a Quiz Topic",
        ["Color Analysis", "Face Shape", "Body Type", "Style Personality", "Wardrobe Essentials"]
    )
    
    if quiz_type == "Color Analysis":
        color_analysis_quiz()
    elif quiz_type == "Face Shape":
        face_shape_quiz()
    elif quiz_type == "Body Type":
        body_type_quiz()
    elif quiz_type == "Style Personality":
        style_personality_quiz()
    elif quiz_type == "Wardrobe Essentials":
        wardrobe_essentials_quiz()

def color_analysis_quiz():
    """Updated quiz with photo upload for automated color analysis"""
    st.markdown("### 🎨 Personal Color Analysis")
    st.markdown("""
        Let's determine your color season using photo analysis! 
        Upload a clear photo of yourself taken in natural lighting with minimal makeup.
    """)
    
    uploaded_file = st.file_uploader(
        "Upload your photo",
        type=['jpg', 'jpeg', 'png'],
        help="For best results, use a photo taken in natural daylight with a neutral background"
    )
    
    if uploaded_file:
        # Display uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Your uploaded photo", width=300)
        
        # Convert image to bytes for API
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()
        
        if st.button("Analyze My Colors", type="primary"):
            with st.spinner("Analyzing your colors..."):
                # Get color analysis from Imagga
                colors_data = analyze_colors_with_imagga(img_byte_arr)
                
                if colors_data:
                    # Determine color season using GPT-4
                    analysis = determine_color_season(colors_data)
                    
                    if analysis:
                        st.markdown(f"""
                            ### 🌟 Your Color Analysis Results
                            
                            **Your Color Season:** {analysis['season']}
                            
                            **Undertone:** {analysis['undertone']}
                            
                            **Most Flattering Colors:**
                            {', '.join(analysis['flattering_colors'])}
                            
                            **Analysis:**
                            {analysis['explanation']}
                        """)
                        
                        # Save results to user profile
                        save_color_analysis(
                            st.session_state.username,
                            analysis
                        )
                        
                        # Show example outfits
                        show_example_outfits(analysis['season'])
                    else:
                        st.error("Could not determine color season. Please try again.")

def save_color_analysis(username, analysis):
    """Save color analysis results to user profile"""
    profile_file = f"{username}_profile.json"
    profile_data = {}
    
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
    
    profile_data['color_analysis'] = {
        'season': analysis['season'],
        'undertone': analysis['undertone'],
        'flattering_colors': analysis['flattering_colors'],
        'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(profile_file, 'w') as f:
        json.dump(profile_data, f, indent=2)

def show_example_outfits(color_season):
    """Show example outfits based on color season"""
    st.markdown("### 👗 Example Outfits for Your Color Season")
    
    # Load user's clothing
    user_clothing = load_user_clothing()
    
    if not user_clothing.empty:
        # Use GPT-4 to suggest outfits from user's wardrobe that match their color season
        prompt = f"""Based on this wardrobe data:
        {user_clothing[['name', 'color', 'type_of_clothing']].to_string()}
        
        Suggest 2-3 outfits that would work well for a {color_season} color season.
        Only include items that actually exist in the wardrobe data.
        Return each outfit as a list of item names, one outfit per line."""
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fashion expert specializing in color analysis."},
                {"role": "user", "content": prompt}
            ]
        )
        
        suggested_outfits = response.choices[0].message.content.strip().split('\n')
        
        for i, outfit in enumerate(suggested_outfits, 1):
            st.markdown(f"#### Outfit {i}")
            
            # Display items in the outfit
            cols = st.columns(3)
            items = [item.strip() for item in outfit.split(',')]
            
            for idx, item_name in enumerate(items):
                matching_item = user_clothing[user_clothing['name'].str.contains(item_name, case=False)]
                
                if not matching_item.empty:
                    with cols[idx % 3]:
                        try:
                            image_path = matching_item.iloc[0]['image_path']
                            if os.path.exists(image_path):
                                image = Image.open(image_path)
                                st.image(image, caption=item_name, use_column_width=True)
                        except Exception as e:
                            st.error(f"Error displaying image for: {item_name}")
            
            # Option to save the outfit
            if st.button(f"Save Outfit {i}", key=f"save_outfit_{i}"):
                # Collect the valid items
                valid_items = []
                for item_name in items:
                    matching_item = user_clothing[user_clothing['name'].str.contains(item_name, case=False)]
                    if not matching_item.empty:
                        item_data = matching_item.iloc[0]
                        valid_items.append({
                            "name": item_data['name'],
                            "image_path": item_data['image_path'],
                            "type_of_clothing": item_data['type_of_clothing'],
                            "color": item_data['color']
                        })
                
                if valid_items:
                    outfit_name = f"Color Season Outfit {datetime.now().strftime('%Y%m%d_%H%M')}"
                    if save_outfit(valid_items, outfit_name, f"{color_season} Season"):
                        st.success(f"✨ Outfit saved as '{outfit_name}'!")
    else:
        st.info("Add some clothes to your wardrobe to see personalized outfit suggestions!")

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
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a color analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    
    try:
        return json.loads(response.choices[0].message.content)
    except:
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
            }
        else:
            st.error(f"API Error: {data.get('status', {}).get('text', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"Error calling Imagga API: {str(e)}")
        return None

def show_color_swatch(hex_color, name):
    """Display a color swatch with name and hex code"""
    st.markdown(f"""
        <div style='
            background-color: {hex_color}; 
            width: 100px; 
            height: 50px; 
            border-radius: 5px;
            margin: 5px;
            display: inline-block;'>
        </div>
        <span style='margin-left: 10px;'>{name} ({hex_color})</span>
    """, unsafe_allow_html=True)

def color_picker_tool():
    """Tool to help users find their skin, hair, and eye color hex codes from photos"""
    st.markdown("### 🎨 Color Picker Tool")
    st.markdown("""
        Upload a clear photo of yourself to automatically detect your:
        - Skin tone
        - Hair color
        - Eye color
        
        **Tips for best results:**
        - Use natural lighting
        - Clear, well-lit photo
        - Minimal makeup
        - Neutral background
    """)
    
    uploaded_file = st.file_uploader("Upload your photo", type=['jpg', 'jpeg', 'png'])
    
    if uploaded_file:
        # Display image
        image = Image.open(uploaded_file)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.image(image, caption="Your Photo", use_column_width=True)
        
        # Extract colors using Imagga API
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_byte_arr = img_byte_arr.getvalue()
        
        with col2:
            st.markdown("### Detected Colors")
            colors = get_image_colors(img_byte_arr)
            
            if colors:
                # Show foreground colors (usually includes skin, hair)
                st.markdown("#### Your Colors")
                for color in colors['foreground'][:5]:  # Show top 5 colors
                    hex_code = color['html_code']
                    name = color['closest_palette_color_name']
                    show_color_swatch(hex_code, name)
                    
                    # Add copy button for hex code
                    if st.button(f"Copy {hex_code}", key=f"copy_{hex_code}"):
                        pyperclip.copy(hex_code)
                        st.success(f"Copied {hex_code} to clipboard!")
                
                # Show all detected colors in expandable section
                with st.expander("View All Detected Colors"):
                    st.markdown("#### All Image Colors")
                    for color in colors['image']:
                        hex_code = color['html_code']
                        name = color['closest_palette_color_name']
                        percentage = color['percent']
                        show_color_swatch(hex_code, f"{name} ({percentage:.1f}%)")

# Main function
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
                "Saved Outfits", "Outfit Calendar", "Style Quizzes"],
               index=["Home", "Image Uploader and Display", "Saved Clothes", 
                      "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
                      "Saved Outfits", "Outfit Calendar", "Style Quizzes"].index(current_page)
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