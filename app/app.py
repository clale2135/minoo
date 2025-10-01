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
import base64  # Add this at the top with other imports
try:
    import pyperclip
except ImportError:
    # Fallback if pyperclip is not available
    class PyperclipFallback:
        def copy(self, text):
            st.code(text, language=None)
    pyperclip = PyperclipFallback()

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)
USER_DB_PATH = "user_db.csv"

# Must be the first Streamlit command
st.set_page_config(
    page_title="greendrobe",
    layout="wide",
    initial_sidebar_state="expanded"
)

def set_custom_style():
   st.markdown("""
       <style>
       /* Add Cooper BT font */
       @font-face {
           font-family: 'Cooper BT';
           src: url('https://db.onlinewebfonts.com/t/05554c33c36c4a1f3a523c1f4bd1637e.woff2') format('woff2'),
                url('https://db.onlinewebfonts.com/t/05554c33c36c4a1f3a523c1f4bd1637e.woff') format('woff');
           font-weight: normal;
           font-style: normal;
       }
       
       /* Add Cooper Hewitt font */
       @font-face {
           font-family: 'Cooper Hewitt';
           src: url('https://db.onlinewebfonts.com/t/c5d7c42f5fab7d4d7c0ee7c3e063c080.woff2') format('woff2'),
                url('https://db.onlinewebfonts.com/t/c5d7c42f5fab7d4d7c0ee7c3e063c080.woff') format('woff');
           font-weight: normal;
           font-style: normal;
       }
       
       /* Darker green theme for greendrobe */
       :root {
           --primary-color: #0D2E1F;      /* Very Dark Forest Green */
           --primary-hover: #1A3D2A;      /* Dark Forest Green */
           --background: #05140A;         /* Almost Black Green */
           --text-color: #E8F5E8;         /* Soft White */
           --border-color: #0D2E1F;       /* Very Dark Forest Green */
           --accent-color: #1F4A35;       /* Dark Green */
           --secondary-color: #2D5A4A;    /* Medium Dark Green */
           --green-gradient: linear-gradient(135deg, #0D2E1F 0%, #1A3D2A 50%, #1F4A35 100%);
           --dark-green-gradient: linear-gradient(135deg, #05140A 0%, #0D2E1F 100%);
       }

       /* Main container styling */
       .stApp {
           background-color: var(--background);
           background-image:
               linear-gradient(rgba(5, 20, 10, 0.95), rgba(13, 46, 31, 0.95)),
               url('https://subtle-patterns.com/patterns/green-fibers.png');
       }
      
       /* Header styling with bubbly text effect */
       .stTitle {
           color: var(--text-color);
           font-family: 'Quicksand', 'Nunito', sans-serif;
           font-weight: 700;
           padding-bottom: 2rem;
           border-bottom: 2px solid var(--border-color);
           margin-bottom: 2rem;
           letter-spacing: 0.5px;
           text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
       }
      
       /* Button styling */
       .stButton > button {
           background: var(--green-gradient);
           color: white;
           border-radius: 20px;
           padding: 0.8rem 1.5rem;
           border: none;
           font-weight: 600;
           letter-spacing: 0.5px;
           text-transform: uppercase;
           font-size: 0.9rem;
           transition: all 0.3s ease;
           box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
       }
      
       .stButton > button:hover {
           transform: translateY(-2px);
           box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3);
           background: var(--primary-hover);
       }
      
       /* Sidebar styling with darker background */
       .css-1d391kg, [data-testid="stSidebar"] {
           background-color: #141f12 !important;
           border-right: 1px solid var(--border-color);
           box-shadow: 2px 0 20px rgba(0, 0, 0, 0.2);
       }
       
       /* All text elements in white */
       div, span, label, .stMarkdown, p, h1, h2, h3, .stTitle, .welcome-msg {
           color: var(--text-color) !important;
       }
       
       /* Card-like containers for clothes with forest theme */
       .clothes-card {
           background-color: rgba(255, 255, 255, 0.1);
           border-radius: 15px;
           padding: 2rem;
           box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
           margin-bottom: 2rem;
           border: 1px solid rgba(41, 59, 34, 0.3);
           transition: all 0.3s ease;
           backdrop-filter: blur(5px);
       }
      
       .clothes-card:hover {
           transform: translateY(-3px);
           box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
           border-color: var(--primary-color);
       }
       
       /* App title - GreenDrobe with Cooper BT font */
       .app-title {
           font-family: 'Cooper BT', 'Cooper Black', 'Georgia', serif;
           font-size: 3.5rem;
           font-weight: 800;
           color: white !important;
           text-align: center;
           margin: 1.5rem 0;
           text-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
           letter-spacing: 1px;
       }
       
       /* Tagline styling with Cooper Hewitt font */
       .app-tagline {
           font-family: 'Cooper Hewitt', 'Helvetica Neue', sans-serif;
           font-size: 1.5rem;
           font-weight: 300;
           color: white !important;
           text-align: center;
           margin-bottom: 2rem;
           letter-spacing: 1px;
       }
       
       /* Welcome message styling */
       .welcome-msg {
           color: var(--text-color);
           text-align: center;
           padding: 2rem 0;
           margin-bottom: 2rem;
           font-size: 1.2rem;
           line-height: 1.8;
           font-family: 'Quicksand', 'Nunito', sans-serif;
           border-bottom: 1px solid var(--border-color);
           text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
       }
       
       /* Input field styling */
       .stTextInput > div > div > input {
           border-radius: 10px;
           border: 1px solid var(--border-color);
           padding: 0.8rem 1rem;
           background-color: rgba(255, 255, 255, 0.1);
           color: white !important;
           transition: all 0.2s ease;
       }
      
       .stTextInput > div > div > input:focus {
           border-color: var(--primary-color);
           box-shadow: 0 0 0 2px rgba(41, 59, 34, 0.2);
           background-color: rgba(255, 255, 255, 0.15);
       }
       
       /* Selectbox styling */
       .stSelectbox > div > div > div {
           background-color: rgba(255, 255, 255, 0.1);
           border: 1px solid var(--border-color);
           border-radius: 10px;
           color: white !important;
       }
       
       /* Multiselect styling */
       .stMultiSelect > div > div > div {
           border-radius: 10px;
           border: 1px solid var(--border-color);
           background-color: rgba(255, 255, 255, 0.1);
           color: white !important;
       }
       
       /* Selected tags in multiselect */
       [data-baseweb="tag"] {
           background-color: var(--primary-color) !important;
           border: none !important;
       }
       
       [data-baseweb="tag"] span {
           color: white !important;
       }
       
       /* Dropdown items */
       [data-baseweb="select"] [role="listbox"],
       [data-baseweb="select"] [role="option"] {
           background-color: #05140A !important;
           color: white !important;
       }
       
       /* Hover state for dropdown options */
       [data-baseweb="select"] [role="option"]:hover {
           background-color: #0D2E1F !important;
       }
       
       /* Keep the rest of your existing styles but update colors as needed */
       // ... existing code ...
       </style>
       
       <!-- Add greendrobe title at the top -->
       <div class="app-title">greendrobe</div>
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
   st.title("Add to Your greendrobe")
  
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
        st.info("Add some clothes to your greendrobe first!")
        return

    user_question = st.text_input(
        "Ask about outfit combinations or styling advice:",
        placeholder="Example: What should I wear for a casual summer day?"
    )

    if st.button("Get Insights"):
        if user_question.strip() == "":
            st.error("Please enter a question.")
        else:
            prompt = f"""Based on this greendrobe data:
            {user_clothing[['name', 'type_of_clothing', 'color', 'occasion', 'season']].to_string()}
            
            Answer the following question by ONLY listing the specific names of items from the greendrobe above.
            Do not add any descriptions or explanations. Just list the item names, one per line.
            
            Question: {user_question}"""

            with st.spinner("Generating outfit suggestions..."):
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a fashion expert. Respond only with the exact names of clothing items from the provided greendrobe, one item per line."},
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
                                    st.rerun()
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
       st.info("Add some clothes to your greendrobe first!")
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
    st.title("🎯 Getting Started with greendrobe")
    
    # Welcome Section
    st.markdown("""
        ### Welcome to greendrobe! 
        Let's walk through how to make the most of your new digital closet.
    """)
    
    # Navigation Guide
    st.markdown("""
        ### 📍 Navigation
        You'll find four main sections in the sidebar:
        1. **Image Uploader and Display** - Add clothes to your greendrobe
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
                - Click 'Save' to add to your greendrobe
            
            **Pro tip**: Take photos of your clothes on a clear background for best results!
        """)
    
    # Managing Clothes Tutorial
    with st.expander("👕 Managing Your greendrobe", expanded=True):
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
    """Run personal attributes quiz, avatar customization, and style quiz in sequence"""
    if 'personal_attributes' not in st.session_state:
        personal_attributes_quiz()
    elif 'avatar_customized' not in st.session_state:
        customize_avatar_and_profile()
    else:
        run_style_quiz()

def generate_dicebear_avatar(avatar_preferences):
    """Generate avatar using DiceBear API"""
    try:
        # Valid hair styles for adventurer
        hair_map = {
            "Short": "short01",
            "Medium": "short02",
            "Long": "short03",
            "Buzz Cut": "short04",
            "Bald": "short05"
        }
        
        # Map color names to hex codes (without #)
        hair_color_map = {
            "black": "000000",
            "brown": "8B4513",
            "blonde": "FFD700",
            "red": "8B0000"
        }
        
        # Map skin tones to hex codes (without #)
        skin_tone_map = {
            "light": "FFE0BD",
            "brown": "C68642",
            "dark": "8D5524"
        }
        
        # Get hex codes for selected colors
        hair_color = hair_color_map.get(avatar_preferences['hair']['color'].lower(), "000000")
        skin_color = skin_tone_map.get(avatar_preferences['skin_tone'].lower(), "FFE0BD")
        
        # Create URL for DiceBear API
        base_url = "https://api.dicebear.com/7.x/adventurer/svg"
        
        # Build options string with valid parameters
        options = {
            "seed": "custom-seed",  # Add some randomness
            "flip": "false",
            "rotate": "0",
            "scale": "100",
            "hair": hair_map.get(avatar_preferences['hair']['length'], "short01"),
            "skinColor": skin_color,
            "hairColor": hair_color,
            "size": "200"
        }
        
        # Convert options to URL parameters
        options_str = "&".join([f"{k}={v}" for k, v in options.items()])
        
        # Construct final URL
        url = f"{base_url}?{options_str}"
        
        # Get the avatar
        response = requests.get(url)
        
        if response.status_code == 200:
            return response.content, url
        else:
            st.error(f"Error generating avatar: {response.status_code} - {response.text}")
            st.error(f"URL attempted: {url}")
            return None, None
            
    except Exception as e:
        st.error(f"Error generating avatar: {str(e)}")
        return None, None

def customize_avatar_and_profile():
    """Allow users to customize their avatar and profile"""
    st.title("🎨 Customize Your Profile")
    
    # Initialize session state for avatar preferences if not exists
    if 'temp_avatar_preferences' not in st.session_state:
        st.session_state.temp_avatar_preferences = {
            "skin_tone": "light",
            "hair": {
                "length": "Short",
                "color": "brown"
            }
        }
    
    # Create two columns for avatar preview and customization
    col_preview, col_customize = st.columns([1, 2])
    
    # Avatar customization outside the form
    with col_customize:
        st.markdown("### Avatar Customization")
        
        # Avatar Base
        col1, col2 = st.columns(2)
        with col1:
            skin_tone = st.select_slider(
                "Skin Tone",
                options=["light", "brown", "dark"],
                value=st.session_state.temp_avatar_preferences["skin_tone"],
                key="skin_tone_slider"
            )
        with col2:
            hair_color = st.select_slider(
                "Hair Color",
                options=["black", "brown", "blonde", "red"],
                value=st.session_state.temp_avatar_preferences["hair"]["color"],
                key="hair_color_slider"
            )
        
        # Hair Style
        hair_length = st.selectbox(
            "Hair Style",
            ["Short", "Medium", "Long", "Buzz Cut", "Bald"],
            index=["Short", "Medium", "Long", "Buzz Cut", "Bald"].index(
                st.session_state.temp_avatar_preferences["hair"]["length"]
            ),
            key="hair_length_select"
        )
    
    # Update temp preferences
    st.session_state.temp_avatar_preferences = {
        "skin_tone": skin_tone,
        "hair": {
            "length": hair_length,
            "color": hair_color
        }
    }
    
    # Preview avatar in the left column
    with col_preview:
        st.markdown("### Avatar Preview")
        avatar_svg, avatar_url = generate_dicebear_avatar(st.session_state.temp_avatar_preferences)
        if avatar_svg:
            st.markdown(avatar_svg.decode(), unsafe_allow_html=True)
    
    # Profile form
    with st.form("profile_form"):
        st.markdown("### Profile Details")
        
        # Style Preferences
        style_keywords = st.multiselect(
            "Select keywords that describe your style",
            ["Classic", "Modern", "Bohemian", "Streetwear", "Minimalist", 
             "Vintage", "Preppy", "Edgy", "Romantic", "Athletic",
             "Elegant", "Casual", "Artistic", "Professional", "Eclectic"],
            max_selections=5
        )
        
        # Favorite Colors
        favorite_colors = st.multiselect(
            "Select your favorite colors to wear",
            ["Black", "White", "Navy", "Gray", "Beige", "Brown",
             "Red", "Blue", "Green", "Yellow", "Purple", "Pink",
             "Orange", "Gold", "Silver"],
            max_selections=5
        )
        
        # Bio
        bio = st.text_area(
            "Write a short bio about your style journey",
            max_chars=200,
            placeholder="Tell us about your style journey, preferences, and goals..."
        )
        
        # Social Media Integration
        st.markdown("#### Social Media (Optional)")
        col8, col9 = st.columns(2)
        with col8:
            instagram = st.text_input("Instagram Handle", placeholder="@username")
        with col9:
            pinterest = st.text_input("Pinterest Username", placeholder="username")
        
        # Style Goals
        style_goals = st.multiselect(
            "What are your style goals?",
            ["Build a capsule greendrobe", "Develop a signature style",
             "Dress more professionally", "Express creativity through fashion",
             "Shop more sustainably", "Mix and match better",
             "Find better-fitting clothes", "Try new styles",
             "Dress more confidently", "Organize greendrobe better"],
            max_selections=3
        )
        
        # Submit button
        submit = st.form_submit_button("Save Profile & Continue to Style Quiz")
        
        if submit:
            # Save final avatar and profile preferences to session state
            st.session_state.avatar_preferences = st.session_state.temp_avatar_preferences
            
            # Generate and save final avatar
            final_avatar_svg, final_avatar_url = generate_dicebear_avatar(st.session_state.avatar_preferences)
            if final_avatar_svg:
                st.session_state.avatar_svg = final_avatar_svg
                st.session_state.avatar_url = final_avatar_url
            
            st.session_state.profile_preferences = {
                "style_keywords": style_keywords,
                "favorite_colors": favorite_colors,
                "bio": bio,
                "social_media": {
                    "instagram": instagram,
                    "pinterest": pinterest
                },
                "style_goals": style_goals
            }
            
            st.session_state.avatar_customized = True
            st.session_state.show_style_quiz = True  # New flag to show quiz
            
            # Show success message
            st.success("Profile saved! Let's discover your style!")
            time.sleep(2)
            st.rerun()

def personal_attributes_quiz():
    """Quiz to gather physical characteristics and preferences"""
    st.title("👤 Personal Attributes Quiz")
    st.markdown("""
        Before we determine your style, let's gather some information about you.
        This will help us provide more personalized style recommendations.
    """)
    
    # Create form for attributes
    with st.form("personal_attributes_form"):
        # Basic Information
        st.markdown("### Basic Information")
        gender = st.selectbox(
            "Gender",
            ["Female", "Male", "Non-binary", "Prefer not to say"]
        )
        
        age = st.number_input(
            "Age",
            min_value=13,
            max_value=120,
            value=25
        )
        
        # Physical Characteristics
        st.markdown("### Physical Characteristics")
        
        # Height in ft/in
        col1, col2 = st.columns(2)
        with col1:
            feet = st.number_input("Height (feet)", min_value=3, max_value=8, value=5)
        with col2:
            inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=6)
        height_value = (feet * 30.48) + (inches * 2.54)  # Store in cm internally
        
        # Weight in lbs
        weight_lbs = st.number_input(
            "Weight (lbs)",
            min_value=66,
            max_value=550,
            value=154
        )
        weight_value = weight_lbs * 0.45359237  # Store in kg internally
        
        # Body Shape Characteristics
        st.markdown("### Body Shape Details")
        shoulder_width = st.select_slider(
            "Shoulder Width",
            options=["Narrow", "Average", "Broad"],
            value="Average"
        )
        
        neck_length = st.select_slider(
            "Neck Length",
            options=["Short", "Average", "Long"],
            value="Average"
        )
        
        leg_length = st.select_slider(
            "Leg Length Proportion",
            options=["Short", "Average", "Long"],
            value="Average"
        )
        
        # Fit Preferences
        st.markdown("### Fit Preferences")
        preferred_fit = st.multiselect(
            "Preferred Clothing Fit",
            ["Loose/Relaxed", "Regular/Classic", "Slim/Fitted", "Oversized"],
            default=["Regular/Classic"]
        )
        
        clothing_comfort = st.multiselect(
            "What's most important in your clothing?",
            ["Comfort", "Style", "Versatility", "Durability", "Easy Care"],
            default=["Comfort", "Style"]
        )
        
        # Areas to highlight/minimize
        st.markdown("### Style Focus")
        highlight_areas = st.multiselect(
            "Areas you'd like to highlight",
            ["Shoulders", "Arms", "Waist", "Legs", "Back", "None"],
            default=["None"]
        )
        
        minimize_areas = st.multiselect(
            "Areas you'd like to minimize",
            ["Shoulders", "Arms", "Waist", "Legs", "Back", "None"],
            default=["None"]
        )
        
        # Submit button
        submit = st.form_submit_button("Continue to Style Quiz")
        
        if submit:
            # Calculate BMI for general body type guidance
            bmi = weight_value / ((height_value/100) ** 2)
            
            # Save all attributes to session state
            st.session_state.personal_attributes = {
                "gender": gender,
                "age": age,
                "height": {
                    "feet": feet,
                    "inches": inches,
                    "cm": height_value  # Store cm for calculations
                },
                "weight": {
                    "lbs": weight_lbs,
                    "kg": weight_value  # Store kg for calculations
                },
                "bmi": bmi,
                "shoulder_width": shoulder_width,
                "neck_length": neck_length,
                "leg_length": leg_length,
                "preferred_fit": preferred_fit,
                "clothing_comfort": clothing_comfort,
                "highlight_areas": highlight_areas,
                "minimize_areas": minimize_areas
            }
            
            # Show success message and rerun to start style quiz
            st.success("Personal attributes saved! Proceeding to style quiz...")
            time.sleep(1)
            st.rerun()  # Changed from experimental_rerun

def run_style_quiz():
    """Run the main style quiz with personal attributes context"""
    # Add custom CSS for better mobile responsiveness
    st.markdown("""
        <style>
        /* Mobile-first responsive design */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            flex-wrap: wrap;
        }
        
        .stTabs [data-baseweb="tab"] {
            flex-grow: 1;
            min-width: 100px;
            white-space: normal;
            padding: 10px 5px;
            font-size: 14px;
        }
        
        /* Custom container for better spacing on mobile */
        .quiz-container {
            padding: 10px;
            margin: 10px 0;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.05);
        }
        
        /* Responsive text sizing */
        @media (max-width: 768px) {
            .quiz-title {
                font-size: 24px !important;
            }
            .quiz-section {
                font-size: 20px !important;
            }
            .quiz-text {
                font-size: 16px !important;
            }
        }
        
        /* Custom styling for multiselect */
        .stMultiSelect [data-baseweb="select"] {
            max-width: 100%;
        }
        
        /* Custom styling for radio buttons */
        .stRadio > label {
            font-size: 14px;
            padding: 8px 0;
        }
        
        /* Progress bar styling */
        .stProgress > div > div {
            height: 15px;
            border-radius: 10px;
        }
        
        /* Button styling */
        .stButton > button {
            width: 100%;
            padding: 12px 24px;
            border-radius: 8px;
            font-weight: 600;
        }
        
        /* Container for better spacing */
        .section-container {
            margin: 15px 0;
            padding: 15px;
            border-radius: 8px;
            background-color: rgba(255, 255, 255, 0.02);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Quiz header with responsive classes
    st.markdown('<h1 class="quiz-title">🎨 Style Personality Quiz</h1>', unsafe_allow_html=True)
    
    with st.form("style_quiz_form"):
        st.markdown("""
            <div class="quiz-text">
                Complete each section to discover your unique style profile.
                Navigate through the tabs below to answer all questions.
            </div>
        """, unsafe_allow_html=True)
        
        # Create responsive tabs
        tab_labels = ["🎨", "👗", "👔", "💍", "🎯"]
        tab_names = ["Colors", "Style", "Clothes", "Accessories", "Goals"]
        
        # Detect screen size using JavaScript
        st.markdown("""
            <script>
                if (window.innerWidth < 768) {
                    // Use emoji-only tabs on mobile
                    document.querySelectorAll('[data-baseweb="tab"]').forEach((tab, index) => {
                        tab.textContent = tab_labels[index];
                    });
                }
            </script>
        """, unsafe_allow_html=True)
        
        tabs = st.tabs(tab_labels)
        
        with tabs[0]:
            st.markdown('<h3 class="quiz-section">Colors & Patterns</h3>', unsafe_allow_html=True)
            
            # Use container for better mobile spacing
            with st.container():
                color_palette = st.selectbox(
                    "Which color palette resonates with you most?",
                    [
                        "Neutrals (Black, White, Gray)",
                        "Earth Tones (Brown, Olive)",
                        "Pastels (Soft Pink, Blue)",
                        "Bold Colors (Red, Blue)",
                        "Monochrome",
                        "Jewel Tones",
                        "Cool Tones",
                        "Warm Tones"
                    ]
                )
                
                pattern_preference = st.multiselect(
                    "Preferred patterns?",
                    [
                        "Solid Colors",
                        "Stripes",
                        "Floral",
                        "Geometric",
                        "Animal Print",
                        "Plaid",
                        "Polka Dots",
                        "Abstract"
                    ],
                    max_selections=3
                )
        
        with tabs[1]:
            st.markdown('<h3 class="quiz-section">Style Inspiration</h3>', unsafe_allow_html=True)
            
            style_icons = st.multiselect(
                "Style icons that inspire you?",
                [
                    "Audrey Hepburn (Classic)",
                    "Kate Moss (Cool)",
                    "David Beckham (Modern)",
                    "Rihanna (Bold)",
                    "Steve Jobs (Minimal)",
                    "Grace Kelly (Timeless)",
                    "Harry Styles (Eclectic)",
                    "Michelle Obama (Polished)"
                ],
                max_selections=2
            )
        
        with tabs[2]:
            st.markdown('<h3 class="quiz-section">Clothing Choices</h3>', unsafe_allow_html=True)
            
            weekend_outfit = st.radio(
                "Ideal weekend outfit?",
                [
                    "Jeans & Tee",
                    "Dress/Skirt",
                    "Athleisure",
                    "Vintage Style",
                    "Tailored Look",
                    "Bohemian"
                ]
            )
            
            workday_style = st.radio(
                "Daily style preference?",
                [
                    "Professional",
                    "Creative",
                    "Casual-Smart",
                    "Trendy",
                    "Classic",
                    "Comfortable"
                ]
            )
        
        with tabs[3]:
            st.markdown('<h3 class="quiz-section">Accessories</h3>', unsafe_allow_html=True)
            
            accessory_preference = st.multiselect(
                "Favorite accessories?",
                [
                    "Statement Jewelry",
                    "Minimal Jewelry",
                    "Scarves",
                    "Belts",
                    "Watches",
                    "Hats",
                    "Bags",
                    "Hair Pieces"
                ],
                max_selections=3
            )
        
        with tabs[4]:
            st.markdown('<h3 class="quiz-section">Style Goals</h3>', unsafe_allow_html=True)
            
            style_goals = st.multiselect(
                "Your style goals?",
                [
                    "Build Versatile greendrobe",
                    "Develop Signature Look",
                    "Stay Trendy",
                    "Express Creativity",
                    "Dress Professionally",
                    "Create Easy Outfits",
                    "Shop Sustainably",
                    "Better Fit"
                ],
                max_selections=3
            )
            
            comfort_style = st.select_slider(
                "Comfort vs. Style?",
                options=["Comfort", "Balanced", "Style"],
                value="Balanced"
            )
        
        # Progress indicator
        filled_fields = sum([
            bool(color_palette),
            bool(pattern_preference),
            bool(style_icons),
            bool(weekend_outfit),
            bool(workday_style),
            bool(accessory_preference),
            bool(style_goals),
            bool(comfort_style)
        ])
        progress = filled_fields / 8
        
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.progress(progress, text=f"Quiz Progress: {int(progress * 100)}%")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Submit button
        submit = st.form_submit_button(
            "✨ Discover My Style ✨",
            use_container_width=True,
            type="primary"
        )
        
        if submit:
            if progress < 1:
                st.error("Please complete all sections!")
            else:
                with st.spinner("✨ Analyzing your style..."):
                    style_preferences = {
                        "color_palette": color_palette,
                        "pattern_preference": pattern_preference,
                        "style_icons": style_icons,
                        "weekend_outfit": weekend_outfit,
                        "workday_style": workday_style,
                        "accessory_preference": accessory_preference,
                        "style_goals": style_goals,
                        "comfort_style": comfort_style
                        # Removed shopping_preference as it's no longer collected
                    }
                    
                    style_aesthetic = analyze_style_preferences(style_preferences)
                    
                    # Save and update
                    save_user_style(st.session_state.username, style_aesthetic)
                    st.session_state.style_aesthetic = style_aesthetic
                    st.session_state.quiz_completed = True
                    st.session_state.show_style_quiz = False
                    st.session_state.show_homepage = True
                    
                    st.success(f"✨ Your style aesthetic is: {style_aesthetic}")
                    time.sleep(2)
                    st.rerun()

def get_body_type_description(bmi):
    """Get a general body type description based on BMI"""
    if bmi < 18.5:
        return "Slim"
    elif bmi < 25:
        return "Regular"
    elif bmi < 30:
        return "Full"
    else:
        return "Bold"

def analyze_style_preferences(preferences):
    """Analyze user's style preferences and return a style aesthetic"""
    try:
        prompt = f"""As a fashion expert, analyze these style preferences and determine the user's primary style aesthetic:
        
        Colors: {preferences['color_palette']}
        Patterns: {', '.join(preferences['pattern_preference'])}
        Style Icons: {', '.join(preferences['style_icons'])}
        Weekend Style: {preferences['weekend_outfit']}
        Work Style: {preferences['workday_style']}
        Accessories: {', '.join(preferences['accessory_preference'])}
        Style Goals: {', '.join(preferences['style_goals'])}
        Comfort vs Style: {preferences['comfort_style']}
        
        Return only one of these style aesthetics:
        - Classic Minimalist
        - Bohemian Free Spirit
        - Modern Professional
        - Trendy Fashion Forward
        - Casual Chic
        - Elegant Sophisticate
        - Eclectic Creative
        - Athletic Luxe
        - Vintage Romantic
        - Contemporary Edge
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a fashion expert. Respond with only one style aesthetic from the given list."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        style_aesthetic = response.choices[0].message.content.strip()
        return style_aesthetic
        
    except Exception as e:
        st.error(f"Error analyzing style preferences: {str(e)}")
        return "Casual Chic"  # Default fallback style

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
    
    prompt = f"""As a fashion expert, suggest an outfit from the user's greendrobe considering:

Current Weather:
- Temperature: {weather_data['temperature']}°C
- Conditions: {weather_data['description']}
- Humidity: {weather_data['humidity']}%
- Wind Speed: {weather_data['wind_speed']} m/s

User's Style: {style_aesthetic}

Available Clothing Items:
{user_clothing[['name', 'type_of_clothing', 'color', 'season']].to_string()}

Suggest an appropriate outfit by listing specific items from their greendrobe that would:
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
                st.info("Add some clothes to your greendrobe first!")
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
    """Display the homepage with GreenDrobe-inspired design"""
    
    # Apply darker green theme
    st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #0f2418;
        color: white;
    }
    .stApp {
        background-color: #0f2418;
    }
    .stSidebar {
        background-color: #0a1a0f;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Hero Section
    st.markdown("""
    <div style="text-align: center; margin-bottom: 4rem; padding: 3rem 0;">
        <h1 style="font-size: 3.5rem; font-weight: 700; color: white; margin-bottom: 1rem; letter-spacing: -0.02em;">
            Welcome to GreenDrobe
        </h1>
        <p style="font-size: 1.5rem; color: #e8f5e8; margin-bottom: 2rem; font-weight: 400;">
            Effortless Looks, Every Day.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sign Up Button
    if not st.session_state.logged_in:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("Sign Up Free/Login", type="primary", use_container_width=True):
                st.session_state.page = "Login/Register"
                st.rerun()
    
    # How It Works Section
    st.markdown("""
    <div style="margin-top: 4rem;">
        <h2 style="text-align: center; font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 3rem;">
            How It Works
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Three Cards Layout
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="
            background-color: #1a3d2a;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📸</div>
            <h3 style="color: white; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                1. Upload Your Clothes
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0;">
                Snap photos of your wardrobe items and let our AI categorize them automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="
            background-color: #1a3d2a;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🤖</div>
            <h3 style="color: white; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                2. Let AI Suggest Outfits
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0;">
                Our AI analyzes your style and creates personalized outfit combinations.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="
            background-color: #1a3d2a;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">💾</div>
            <h3 style="color: white; font-size: 1.5rem; font-weight: 600; margin-bottom: 1rem;">
                3. Save or Share Your Look
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0;">
                Save your favorite outfits, schedule them for specific days, or share with friends.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features & Benefits Section
    st.markdown("""
    <div style="margin-top: 4rem;">
        <h2 style="text-align: center; font-size: 2.5rem; font-weight: 700; color: white; margin-bottom: 3rem;">
            Features & Benefits
        </h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Features Grid (3x2)
    # Row 1
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🧠</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Smart Outfit Recommendations
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Our AI learns your style preferences and suggests outfits that match your taste.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col2:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🌤️</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Weather-Based Suggestions
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Get outfit ideas that are appropriate for the current weather in your location.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col3:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">👔</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Closet Organization
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Categorize and filter your clothes by type, color, season, and occasion.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Row 2
    feat_col4, feat_col5, feat_col6 = st.columns(3)
    
    with feat_col4:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📅</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Daily Outfit Planner
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Schedule outfits for specific days and never worry about what to wear.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col5:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📱</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Easy-to-Use Interface
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Intuitive design makes managing your wardrobe simple and enjoyable.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    with feat_col6:
        st.markdown("""
        <div style="
            background-color: #2d5a3d;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="font-size: 3rem; margin-bottom: 1rem;">🔄</div>
            <h3 style="color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem;">
                Outfit Challenges
            </h3>
            <p style="color: #e8f5e8; line-height: 1.6; margin: 0; font-size: 0.95rem;">
                Participate in style challenges to discover new ways to wear your clothes.
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # User Stats Section (if logged in)
    if st.session_state.logged_in:
        st.markdown("""
        <div style="margin-top: 3rem; text-align: center;">
            <h3 style="color: white; font-size: 1.8rem; font-weight: 600; margin-bottom: 2rem;">
                Welcome back, """ + st.session_state.username + """! 👋
            </h3>
        </div>
        """, unsafe_allow_html=True)
        
        user_clothing = load_user_clothing()
        if not user_clothing.empty:
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("👕 Items", len(user_clothing))
            with col_b:
                st.metric("🏷️ Types", user_clothing['type_of_clothing'].nunique())
            with col_c:
                st.metric("🎨 Colors", user_clothing['color'].nunique())
        else:
            st.info("📸 Upload your first item to get started! 🚀")
    

def get_user_style():
    """Get user's style from their profile"""
    profile_file = f"{st.session_state.username}_profile.json"
    if os.path.exists(profile_file):
        with open(profile_file, 'r') as f:
            profile_data = json.load(f)
            return profile_data.get('style_aesthetic', 'Not set')
    return "Not set"


def show_wardrobe_stats():
    """Display user's greendrobe statistics"""
    user_clothing = load_user_clothing()
    
    if not user_clothing.empty:
        st.markdown("### 📊 Your greendrobe Stats")
        
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
        st.info("Add some clothes to your greendrobe to see statistics!")


def style_quizzes():
    """Interactive quizzes for personal style education"""
    st.title("📚 Style Education & Quizzes")
    
    # Quiz Selection
    quiz_type = st.selectbox(
        "Choose a Quiz Topic",
        ["Color Analysis", "Face Shape", "Body Type", "Style Personality", "greendrobe Essentials"]
    )
    
    if quiz_type == "Color Analysis":
        color_analysis_quiz()
    elif quiz_type == "Face Shape":
        face_shape_quiz()
    elif quiz_type == "Body Type":
        body_type_quiz()
    elif quiz_type == "Style Personality":
        style_personality_quiz()
    elif quiz_type == "greendrobe Essentials":
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
        # Use GPT-4 to suggest outfits from user's greendrobe that match their color season
        prompt = f"""Based on this greendrobe data:
        {user_clothing[['name', 'color', 'type_of_clothing']].to_string()}
        
        Suggest 2-3 outfits that would work well for a {color_season} color season.
        Only include items that actually exist in the greendrobe data.
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
        st.info("Add some clothes to your greendrobe to see personalized outfit suggestions!")

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
            'question': "How do you approach color in your greendrobe?",
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
                "Capsule greendrobe with easy mixing",
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
            This is your dominant style preference and should guide most of your greendrobe choices.
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
    
    tabs = st.tabs(["greendrobe Essentials", "Color Palette", "Styling Tips", "Shopping Guide"])
    
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
        st.markdown("#### Shopping Recommendation")
        st.markdown(recommendations['shopping_guide'])
    
    # Action steps
    st.markdown("### Next Steps")
    st.markdown("""
        1. Review your current greendrobe against these recommendations
        2. Identify gaps in your greendrobe essentials
        3. Plan your next shopping trip based on the guidelines
        4. Experiment with combining your primary and secondary styles
    """)

def get_style_recommendations(primary, secondary):
    """Get detailed style recommendations based on style combination"""
    prompt = f"""Create detailed style recommendations for someone with:
    Primary Style: {primary}
    Secondary Style: {secondary}
    
    Include:
    1. List of 10 greendrobe essentials
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
    st.markdown("### 👔 greendrobe Essentials Quiz")
    st.markdown("""
        Let's identify the key pieces you need based on your lifestyle and preferences.
        This will help you build a functional and versatile greendrobe.
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
    """Analyze quiz responses to determine greendrobe essentials"""
    prompt = f"""Based on these factors:
    Lifestyle: {responses['lifestyle']}
    Climate: {responses['climate']}
    Priorities: {responses['priorities']}
    
    Create a list of 10 essential greendrobe pieces that would best serve this person.
    Return the list with each item on a new line."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a greendrobe planning expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().split('\n')

def show_wardrobe_essentials_results(essentials):
    """Display greendrobe essentials results"""
    st.success("Your greendrobe Essentials")
    
    st.markdown("### Must-Have Pieces")
    for i, item in enumerate(essentials, 1):
        st.markdown(f"{i}. {item}")
    
    st.markdown("### Building Your greendrobe")
    st.markdown("""
        Tips for collecting your essentials:
        - Focus on quality over quantity
        - Choose versatile pieces that work together
        - Consider your color palette
        - Invest in good basics first
        - Add statement pieces gradually
    """)
    
    # Check against current greendrobe
    user_clothing = load_user_clothing()
    if not user_clothing.empty:
        st.markdown("### greendrobe Gap Analysis")
        missing_items = []
        for essential in essentials:
            # Check if any similar items exist in greendrobe
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
            'question': "How do you approach color in your greendrobe?",
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
                "Capsule greendrobe with easy mixing",
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
            This is your dominant style preference and should guide most of your greendrobe choices.
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
    
    tabs = st.tabs(["greendrobe Essentials", "Color Palette", "Styling Tips", "Shopping Guide"])
    
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
        1. Review your current greendrobe against these recommendations
        2. Identify gaps in your greendrobe essentials
        3. Plan your next shopping trip based on the guidelines
        4. Experiment with combining your primary and secondary styles
    """)

def get_style_recommendations(primary, secondary):
    """Get detailed style recommendations based on style combination"""
    prompt = f"""Create detailed style recommendations for someone with:
    Primary Style: {primary}
    Secondary Style: {secondary}
    
    Include:
    1. List of 10 greendrobe essentials
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
    st.markdown("### 👔 greendrobe Essentials Quiz")
    st.markdown("""
        Let's identify the key pieces you need based on your lifestyle and preferences.
        This will help you build a functional and versatile greendrobe.
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
    """Analyze quiz responses to determine greendrobe essentials"""
    prompt = f"""Based on these factors:
    Lifestyle: {responses['lifestyle']}
    Climate: {responses['climate']}
    Priorities: {responses['priorities']}
    
    Create a list of 10 essential greendrobe pieces that would best serve this person.
    Return the list with each item on a new line."""
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a greendrobe planning expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip().split('\n')

def show_wardrobe_essentials_results(essentials):
    """Display greendrobe essentials results"""
    st.success("Your greendrobe Essentials")
    
    st.markdown("### Must-Have Pieces")
    for i, item in enumerate(essentials, 1):
        st.markdown(f"{i}. {item}")
    
    st.markdown("### Building Your greendrobe")
    st.markdown("""
        Tips for collecting your essentials:
        - Focus on quality over quantity
        - Choose versatile pieces that work together
        - Consider your color palette
        - Invest in good basics first
        - Add statement pieces gradually
    """)
    
    # Check against current greendrobe
    user_clothing = load_user_clothing()
    if not user_clothing.empty:
        st.markdown("### greendrobe Gap Analysis")
        missing_items = []
        for essential in essentials:
            # Check if any similar items exist in greendrobe
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

def display_profile(username):
    """Display user profile with avatar"""
    if 'avatar_svg' in st.session_state and 'profile_preferences' in st.session_state:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.markdown("### Your Avatar")
            st.markdown(st.session_state.avatar_svg.decode(), unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Profile Details")
            prefs = st.session_state.profile_preferences
            
            st.markdown(f"**Style Keywords:** {', '.join(prefs['style_keywords'])}")
            st.markdown(f"**Favorite Colors:** {', '.join(prefs['favorite_colors'])}")
            st.markdown(f"**Bio:** {prefs['bio']}")
            
            if prefs['social_media']['instagram'] or prefs['social_media']['pinterest']:
                st.markdown("#### Social Media")
                if prefs['social_media']['instagram']:
                    st.markdown(f"📸 Instagram: {prefs['social_media']['instagram']}")
                if prefs['social_media']['pinterest']:
                    st.markdown(f"📌 Pinterest: {prefs['social_media']['pinterest']}")
            
            st.markdown("#### Style Goals")
            for goal in prefs['style_goals']:
                st.markdown(f"- {goal}")

# def shopping_recommendations():
#     """Generate personalized shopping recommendations"""
#     st.title("🛍️ Shopping Recommendations")
#     
#     # Load user's greendrobe
#     user_clothing = load_user_clothing()
#     
#     if user_clothing.empty:
#         st.warning("Please add some clothes to your greendrobe first to get personalized recommendations!")
#         st.markdown("[Go to Image Uploader and Display →](Image Uploader and Display)")
#         return
#     
#     # Create tabs for different recommendation types
#     tab1, tab2, tab3 = st.tabs([
#         "Based on Your Style",
#         "Fill greendrobe Gaps",
#         "Trending Items"
#     ])
#     
#     with tab1:
#         style_based_recommendations(user_clothing)
#     
#     with tab2:
#         greendrobe_gap_recommendations(user_clothing)
#     
#     with tab3:
#         trending_recommendations()

# def style_based_recommendations(user_clothing):
#     """Generate recommendations based on user's style"""
#     st.header("Recommendations Based on Your Style")
#     
#     # Analyze user's style preferences
#     clothing_types = user_clothing['type_of_clothing'].value_counts()
#     colors = user_clothing['color'].value_counts()
#     
#     # Display style analysis
#     col1, col2 = st.columns(2)
#     
#     with col1:
#         st.subheader("Your Most Common Items")
#         if not clothing_types.empty:
#             st.bar_chart(clothing_types)
#     
#     with col2:
#         st.subheader("Your Color Preferences")
#         if not colors.empty:
#             st.bar_chart(colors)
#     
#     # Generate recommendations
#     st.subheader("Recommended Items")
#     
#     # Example recommendations based on user's preferences
#     recommendations = [
#         {
#             "name": "Classic White T-Shirt",
#             "type": "T-shirt",
#             "price": "$25",
#             "description": "A versatile addition to your greendrobe",
#             "link": "https://example.com/shirt"
#         },
#         {
#             "name": "Dark Blue Jeans",
#             "type": "Jeans",
#             "price": "$60",
#             "description": "Perfect for casual outfits",
#             "link": "https://example.com/jeans"
#         },
#         # Add more recommendations as needed
#     ]
#     
#     # Display recommendations in a grid
#     cols = st.columns(3)
#     for idx, item in enumerate(recommendations):
#         with cols[idx % 3]:
#             st.markdown(f"### {item['name']}")
#             st.markdown(f"**Type:** {item['type']}")
#             st.markdown(f"**Price:** {item['price']}")
#             st.markdown(f"**Description:** {item['description']}")
#             st.markdown(f"[Shop Now]({item['link']})")

def wardrobe_gap_recommendations(user_clothing):
    """Identify and recommend items to fill greendrobe gaps"""
    st.header("Fill Your greendrobe Gaps")
    
    # Define essential greendrobe items
    essential_items = {
        "Tops": ["T-shirt", "Blouse", "Sweater"],
        "Bottoms": ["Jeans", "Pants", "Skirt"],
        "Outerwear": ["Jacket", "Coat"],
        "Dresses": ["Dress"],
        "Shoes": ["Shoes"]
    }
    
    # Check what user has
    user_items = set(user_clothing['type_of_clothing'].unique())
    
    # Find gaps
    gaps = {}
    for category, items in essential_items.items():
        missing_items = [item for item in items if item not in user_items]
        if missing_items:
            gaps[category] = missing_items
    
    # Display gaps and recommendations
    if gaps:
        st.markdown("### Missing Essential Items")
        for category, missing in gaps.items():
            st.markdown(f"**{category}:** {', '.join(missing)}")
            
            # Example recommendations for missing items
            st.markdown("#### Recommended Items")
            cols = st.columns(len(missing))
            for idx, item in enumerate(missing):
                with cols[idx]:
                    st.markdown(f"##### {item}")
                    st.markdown("Price: $XX")
                    st.markdown("[Shop Now](https://example.com)")
    else:
        st.success("Great! Your greendrobe contains all essential items!")

def trending_recommendations():
    """Show trending fashion items"""
    st.header("Trending Fashion Items")
    
    # Example trending categories
    trending_categories = [
        "Sustainable Fashion",
        "Vintage Inspired",
        "Minimalist Basics",
        "Statement Pieces"
    ]
    
    # Display trending categories
    selected_category = st.selectbox(
        "Choose a trending category",
        trending_categories
    )
    
    # Example trending items
    trending_items = {
        "Sustainable Fashion": [
            {"name": "Organic Cotton Tee", "price": "$30"},
            {"name": "Recycled Denim Jeans", "price": "$80"},
            {"name": "Eco-friendly Sneakers", "price": "$70"}
        ],
        "Vintage Inspired": [
            {"name": "Retro Print Dress", "price": "$65"},
            {"name": "High-Waisted Pants", "price": "$55"},
            {"name": "Vintage Style Blouse", "price": "$45"}
        ],
        "Minimalist Basics": [
            {"name": "Classic White Shirt", "price": "$40"},
            {"name": "Black Slim Pants", "price": "$50"},
            {"name": "Basic Blazer", "price": "$90"}
        ],
        "Statement Pieces": [
            {"name": "Printed Kimono", "price": "$75"},
            {"name": "Bold Pattern Skirt", "price": "$60"},
            {"name": "Colorful Jacket", "price": "$85"}
        ]
    }
    
    # Display trending items for selected category
    if selected_category in trending_items:
        cols = st.columns(3)
        for idx, item in enumerate(trending_items[selected_category]):
            with cols[idx]:
                st.markdown(f"### {item['name']}")
                st.markdown(f"**Price:** {item['price']}")
                st.markdown("[Shop Now](https://example.com)")

def trading_marketplace():
    """Marketplace for users to trade or share clothing items"""
    st.title("👕 Trading Marketplace")
    
    # Check if user is logged in
    if "username" not in st.session_state:
        st.warning("Please log in to access the Trading Marketplace")
        return
        
    # Create tabs for different marketplace functions
    tab1, tab2, tab3 = st.tabs(["Browse Items", "List Item", "My Listings"])
    
    with tab1:
        st.markdown("### Available Items")
        # Load all available items from marketplace
        marketplace_items = load_marketplace_items()
        
        if marketplace_items.empty:
            st.info("No items currently listed in the marketplace")
        else:
            # Display items in grid layout
            items_per_row = 3
            for i in range(0, len(marketplace_items), items_per_row):
                cols = st.columns(items_per_row)
                for j, col in enumerate(cols):
                    if i + j < len(marketplace_items):
                        item = marketplace_items.iloc[i + j]
                        with col:
                            if os.path.exists(item['image_path']):
                                st.image(item['image_path'], caption=item['name'])
                                st.write(f"**{item['name']}**")
                                st.write(f"Listed by: {item['owner']}")
                                st.write(f"Status: {item['status']}")
                                
                                if item['owner'] != st.session_state.username:
                                    if st.button("Request Trade", key=f"trade_{item['id']}"):
                                        initiate_trade_request(item['id'])
                                        st.success("Trade request sent!")
    
    with tab2:
        st.markdown("### List an Item for Trade")
        # Load user's clothing items
        user_clothing = load_user_clothing()
        
        if user_clothing.empty:
            st.info("Add items to your greendrobe first!")
        else:
            # Form for listing item
            with st.form("list_item_form"):
                selected_item = st.selectbox(
                    "Select item to list",
                    user_clothing['name'].tolist()
                )
                
                trade_preferences = st.multiselect(
                    "What would you like in return?",
                    ["Shirts", "Pants", "Dresses", "Shoes", "Accessories"],
                    max_selections=3
                )
                
                description = st.text_area(
                    "Additional notes",
                    placeholder="Add any details about condition, size, etc."
                )
                
                if st.form_submit_button("List Item"):
                    if list_item_for_trade(selected_item, trade_preferences, description):
                        st.success("Item listed successfully!")
                        st.rerun()
    
    with tab3:
        st.markdown("### My Listed Items")
        # Load user's listed items
        my_listings = load_user_listings()
        
        if my_listings.empty:
            st.info("You haven't listed any items yet")
        else:
            for _, item in my_listings.iterrows():
                with st.expander(item['name']):
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        if os.path.exists(item['image_path']):
                            st.image(item['image_path'])
                    with col2:
                        st.write(f"**Status:** {item['status']}")
                        st.write(f"**Listed on:** {item['list_date']}")
                        st.write(f"**Trade preferences:** {', '.join(item['trade_preferences'])}")
                        
                        if st.button("Remove Listing", key=f"remove_{item['id']}"):
                            remove_listing(item['id'])
                            st.success("Listing removed")
                            st.rerun()

def load_marketplace_items():
    """Load all available items in the marketplace"""
    marketplace_file = "marketplace.csv"
    if os.path.exists(marketplace_file):
        return pd.read_csv(marketplace_file)
    return pd.DataFrame(columns=['id', 'name', 'owner', 'image_path', 'status', 'trade_preferences', 'list_date'])

def list_item_for_trade(item_name, trade_preferences, description):
    """Add an item to the marketplace"""
    try:
        marketplace_items = load_marketplace_items()
        user_clothing = load_user_clothing()
        
        item = user_clothing[user_clothing['name'] == item_name].iloc[0]
        
        new_listing = pd.DataFrame([{
            'id': str(uuid.uuid4()),
            'name': item_name,
            'owner': st.session_state.username,
            'image_path': item['image_path'],
            'status': 'Available',
            'trade_preferences': json.dumps(trade_preferences),
            'description': description,
            'list_date': datetime.now().strftime("%Y-%m-%d")
        }])
        
        marketplace_items = pd.concat([marketplace_items, new_listing], ignore_index=True)
        marketplace_items.to_csv("marketplace.csv", index=False)
        return True
        
    except Exception as e:
        st.error(f"Error listing item: {str(e)}")
        return False

def load_user_listings():
    """Load listings for the current user"""
    marketplace_items = load_marketplace_items()
    return marketplace_items[marketplace_items['owner'] == st.session_state.username]

def remove_listing(listing_id):
    """Remove an item from the marketplace"""
    marketplace_items = load_marketplace_items()
    marketplace_items = marketplace_items[marketplace_items['id'] != listing_id]
    marketplace_items.to_csv("marketplace.csv", index=False)

def initiate_trade_request(listing_id):
    """
    Initiate a trade request for a marketplace item
    
    Args:
        listing_id (str): ID of the marketplace listing being requested
    """
    try:
        # Load necessary data
        marketplace_items = load_marketplace_items()
        user_clothing = load_user_clothing()
        
        # Get the listing details
        listing = marketplace_items[marketplace_items['id'] == listing_id].iloc[0]
        
        # Create trade request file path
        trade_requests_file = "trade_requests.csv"
        
        # Load existing trade requests or create new DataFrame
        if os.path.exists(trade_requests_file):
            trade_requests = pd.read_csv(trade_requests_file)
        else:
            trade_requests = pd.DataFrame(columns=[
                'request_id', 'listing_id', 'requester', 'owner',
                'status', 'request_date', 'offered_items', 'notes'
            ])
        
        # Check if user already has a pending request for this item
        existing_request = trade_requests[
            (trade_requests['listing_id'] == listing_id) & 
            (trade_requests['requester'] == st.session_state.username) &
            (trade_requests['status'] == 'Pending')
        ]
        
        if not existing_request.empty:
            st.warning("You already have a pending request for this item!")
            return False
        
        # Create form for trade request
        st.markdown("### Trade Request")
        with st.form("trade_request_form"):
            # Let user select items to offer
            available_items = user_clothing['name'].tolist()
            offered_items = st.multiselect(
                "Select items to offer in trade",
                available_items,
                max_selections=3
            )
            
            # Add notes for the trade
            notes = st.text_area(
                "Add a message to the owner",
                placeholder="Explain why you're interested in trading, ask questions, etc."
            )
            
            # Submit button
            submitted = st.form_submit_button("Send Trade Request")
            
            if submitted:
                if not offered_items:
                    st.error("Please select at least one item to offer!")
                    return False
                
                # Create new trade request
                new_request = pd.DataFrame([{
                    'request_id': str(uuid.uuid4()),
                    'listing_id': listing_id,
                    'requester': st.session_state.username,
                    'owner': listing['owner'],
                    'status': 'Pending',
                    'request_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'offered_items': json.dumps(offered_items),
                    'notes': notes
                }])
                
                # Add to trade requests
                trade_requests = pd.concat([trade_requests, new_request], ignore_index=True)
                trade_requests.to_csv(trade_requests_file, index=False)
                
                # Update listing status
                marketplace_items.loc[marketplace_items['id'] == listing_id, 'status'] = 'Pending Trade'
                marketplace_items.to_csv("marketplace.csv", index=False)
                
                # Send notification to owner (placeholder for future implementation)
                notify_owner_of_trade_request(listing['owner'], listing_id)
                
                return True
        
    except Exception as e:
        st.error(f"Error initiating trade request: {str(e)}")
        return False

def notify_owner_of_trade_request(owner_username, listing_id):
    """
    Notify the owner of a new trade request (placeholder implementation)
    
    Args:
        owner_username (str): Username of the item owner
        listing_id (str): ID of the listing
    """
    # Create notifications file path
    notifications_file = f"{owner_username}_notifications.json"
    
    try:
        # Load existing notifications or create new list
        if os.path.exists(notifications_file):
            with open(notifications_file, 'r') as f:
                notifications = json.load(f)
        else:
            notifications = []
        
        # Add new notification
        notifications.append({
            'type': 'trade_request',
            'listing_id': listing_id,
            'requester': st.session_state.username,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'read': False
        })
        
        # Save notifications
        with open(notifications_file, 'w') as f:
            json.dump(notifications, f, indent=2)
            
    except Exception as e:
        st.warning(f"Could not send notification: {str(e)}")

def add_social_features():
    """Add social media features to the sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌟 Social Features")
    
    # Navigation for social features
    social_option = st.sidebar.selectbox(
        "Social Navigation",
        ["Feed", "My Profile", "Find Users", "Saved Posts"],
        key="social_nav"
    )
    
    # Display the selected social feature
    if social_option == "Feed":
        show_social_feed()
    elif social_option == "My Profile":
        show_user_profile()
    elif social_option == "Find Users":
        find_users()
    elif social_option == "Saved Posts":
        show_saved_posts()

def show_social_feed():
    """Display the social feed with posts from followed users"""
    st.title("👗 Style Feed")
    
    # Create a new post
    with st.expander("✨ Create New Post"):
        create_new_post()
    
    social_data = load_social_data()
    posts = social_data.get("posts", [])
    follows = social_data.get("follows", {}).get(st.session_state.username, [])
    
    # Filter posts to show only from followed users and self
    relevant_posts = [
        post for post in posts 
        if post["user_id"] in follows or post["user_id"] == st.session_state.username
    ]
    
    if not relevant_posts:
        st.info("Follow some users to see their posts here!")
        return
    
    # Display posts
    for post in relevant_posts:
        display_post(post)

def show_user_profile():
    """Display user profile with their posts and stats"""
    st.title(f"👤 {st.session_state.username}'s Profile")
    
    social_data = load_social_data()
    user_posts = [
        post for post in social_data.get("posts", [])
        if post["user_id"] == st.session_state.username
    ]
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Posts", len(user_posts))
    with col2:
        followers = len([
            u for u, f in social_data.get("follows", {}).items()
            if st.session_state.username in f
        ])
        st.metric("Followers", followers)
    with col3:
        following = len(
            social_data.get("follows", {}).get(st.session_state.username, [])
        )
        st.metric("Following", following)
    
    # Display user's posts
    st.markdown("### My Posts")
    for post in user_posts:
        display_post(post)

def find_users():
    """Interface for finding and following other users"""
    st.title("🔍 Find Users")
    
    # Load all users
    df = load_user_db()
    social_data = load_social_data()
    following = social_data.get("follows", {}).get(st.session_state.username, [])
    
    # Search interface
    search = st.text_input("Search users...")
    
    for _, user in df.iterrows():
        username = user["username"]
        if username != st.session_state.username and (
            not search or search.lower() in username.lower()
        ):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"👤 {username}")
            with col2:
                if username in following:
                    if st.button("Unfollow", key=f"unfollow_{username}"):
                        toggle_follow(username)
                        st.rerun()
                else:
                    if st.button("Follow", key=f"follow_{username}"):
                        toggle_follow(username)
                        st.rerun()

def show_saved_posts():
    """Display saved posts"""
    st.title("📚 Saved Posts")
    
    social_data = load_social_data()
    saved_posts = social_data.get("saved_posts", {}).get(st.session_state.username, [])
    
    if not saved_posts:
        st.info("You haven't saved any posts yet!")
        return
    
    # Display saved posts
    for post_id in saved_posts:
        post = next(
            (p for p in social_data.get("posts", []) if p["id"] == post_id),
            None
        )
        if post:
            display_post(post)

def create_new_post():
    """Interface for creating a new post"""
    with st.form("new_post_form"):
        content = st.text_area("Share your style thoughts...", max_chars=500)
        
        # Option to attach outfit
        user_outfits = load_user_outfits()
        outfit_options = ["None"] + [outfit["name"] for outfit in user_outfits]
        selected_outfit = st.selectbox("Share an outfit", outfit_options)
        
        # Upload images
        uploaded_files = st.file_uploader(
            "Add photos",
            accept_multiple_files=True,
            type=["jpg", "jpeg", "png"]
        )
        
        if st.form_submit_button("Post"):
            if not content and not uploaded_files and selected_outfit == "None":
                st.error("Please add some content, photos, or select an outfit to share!")
                return
            
            # Save uploaded images
            image_paths = []
            if uploaded_files:
                for file in uploaded_files:
                    # Create uploads directory if it doesn't exist
                    os.makedirs("uploads", exist_ok=True)
                    
                    # Generate unique filename
                    save_path = f"uploads/social_{uuid.uuid4()}_{file.name}"
                    
                    # Save the file
                    with open(save_path, "wb") as f:
                        f.write(file.getbuffer())
                    image_paths.append(save_path)
            
            # Add outfit images if selected
            outfit_id = None
            if selected_outfit != "None":
                outfit = next((o for o in user_outfits if o["name"] == selected_outfit), None)
                if outfit:
                    outfit_id = outfit["id"]
                    image_paths.extend([item["image_path"] for item in outfit["items"]])
            
            # Create post
            post = create_post(
                st.session_state.username,
                content,
                image_paths,
                outfit_id
            )
            
            st.success("Post created successfully!")
            st.rerun()

def load_user_outfits():
    """Load user's saved outfits"""
    outfit_file = f"{st.session_state.username}_outfits.json"
    try:
        if os.path.exists(outfit_file):
            with open(outfit_file, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading outfits: {str(e)}")
    return []

def create_post(user_id, content, image_paths, outfit_id=None):
    """Create a new social post"""
    social_data = load_social_data()
    
    # Initialize posts list if it doesn't exist
    if "posts" not in social_data:
        social_data["posts"] = []
    
    new_post = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "content": content,
        "image_paths": image_paths,
        "likes": 0,
        "comments": [],
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "outfit_id": outfit_id
    }
    
    # Add post to the beginning of the list
    social_data["posts"].insert(0, new_post)
    save_social_data(social_data)
    return new_post

def load_social_data():
    """Load social data from JSON file"""
    social_file = "social_data.json"
    try:
        if os.path.exists(social_file):
            with open(social_file, 'r') as f:
                return json.load(f)
        else:
            # Initialize default structure if file doesn't exist
            default_data = {
                "posts": [],
                "follows": {},
                "likes": {},
                "comments": {},
                "saved_posts": {}
            }
            save_social_data(default_data)
            return default_data
    except Exception as e:
        st.error(f"Error loading social data: {str(e)}")
        return {
            "posts": [],
            "follows": {},
            "likes": {},
            "comments": {},
            "saved_posts": {}
        }

def save_social_data(data):
    """Save social data to JSON file"""
    social_file = "social_data.json"
    try:
        # Ensure the data has all required keys
        required_keys = ["posts", "follows", "likes", "comments", "saved_posts"]
        for key in required_keys:
            if key not in data:
                data[key] = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(social_file) if os.path.dirname(social_file) else '.', exist_ok=True)
        
        # Save the data
        with open(social_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Error saving social data: {str(e)}")

def display_post(post):
    """Display a single post with interactions"""
    with st.container():
        # Post header with user info and timestamp
        st.markdown(f"""
            <div style='
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            '>
                <h4 style='margin: 0;'>👤 {post['user_id']}</h4>
                <p style='color: #666; font-size: 0.8em; margin: 5px 0;'>
                    {post['created_at']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Post content
        if post.get('content'):
            st.markdown(f"<p style='margin: 15px 0;'>{post['content']}</p>", unsafe_allow_html=True)
        
        # Display images in a grid
        if post.get('image_paths'):
            valid_images = [path for path in post['image_paths'] if os.path.exists(path)]
            if valid_images:
                cols = st.columns(min(3, len(valid_images)))
                for idx, img_path in enumerate(valid_images):
                    try:
                        with cols[idx % 3]:
                            st.image(img_path, use_column_width=True)
                    except Exception as e:
                        st.error(f"Error displaying image: {str(e)}")
        
        # Interaction buttons
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            # Like button
            social_data = load_social_data()
            like_key = f"{st.session_state.username}_{post['id']}"
            is_liked = like_key in social_data.get("likes", {})
            like_icon = "❤️" if is_liked else "🤍"
            
            if st.button(
                f"{like_icon} {post.get('likes', 0)}",
                key=f"like_{post['id']}"
            ):
                toggle_like(post['id'])
                st.rerun()
        
        with col2:
            # Comment button
            if st.button(
                "💬 Comment",
                key=f"comment_{post['id']}"
            ):
                st.session_state.commenting_on = post['id']
        
        with col3:
            # Save post button
            saved_posts = social_data.get("saved_posts", {}).get(st.session_state.username, [])
            is_saved = post['id'] in saved_posts
            save_icon = "📑" if is_saved else "🔖"
            save_text = "Saved" if is_saved else "Save"
            
            if st.button(
                f"{save_icon} {save_text}",
                key=f"save_{post['id']}"
            ):
                toggle_save_post(post['id'])
                st.rerun()
        
        # Comment section
        if st.session_state.get('commenting_on') == post['id']:
            with st.form(f"comment_form_{post['id']}"):
                comment = st.text_input("Add a comment...")
                if st.form_submit_button("Post Comment"):
                    if add_comment(post['id'], comment):
                        st.session_state.commenting_on = None
                        st.rerun()

        # Display existing comments
        comments = get_post_comments(post['id'])
        if comments:
            with st.expander(f"View {len(comments)} comments"):
                for comment in comments:
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                                <strong>{comment['user_id']}</strong>: {comment['content']}
                                <br><small style='color: #666;'>{comment['created_at']}</small>
                            </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if comment['user_id'] == st.session_state.username:
                            if st.button("🗑️", key=f"delete_comment_{comment['id']}"):
                                if delete_comment(post['id'], comment['id']):
                                    st.rerun()

def toggle_save_post(post_id):
    """Toggle save/unsave status for a post"""
    social_data = load_social_data()
    
    if "saved_posts" not in social_data:
        social_data["saved_posts"] = {}
    
    if st.session_state.username not in social_data["saved_posts"]:
        social_data["saved_posts"][st.session_state.username] = []
    
    user_saved_posts = social_data["saved_posts"][st.session_state.username]
    
    if post_id in user_saved_posts:
        user_saved_posts.remove(post_id)
    else:
        user_saved_posts.append(post_id)
    
    save_social_data(social_data)

def toggle_follow(target_user):
    """Toggle following status for a user"""
    try:
        social_data = load_social_data()
        
        # Initialize follows dictionary if it doesn't exist
        if "follows" not in social_data:
            social_data["follows"] = {}
        
        # Initialize current user's following list if it doesn't exist
        if st.session_state.username not in social_data["follows"]:
            social_data["follows"][st.session_state.username] = []
        
        following = social_data["follows"][st.session_state.username]
        
        # Toggle follow status
        if target_user in following:
            # Unfollow
            following.remove(target_user)
            st.toast(f"Unfollowed {target_user}", icon="👋")
        else:
            # Follow
            following.append(target_user)
            st.toast(f"Following {target_user}", icon="✨")
        
        # Save updated social data
        save_social_data(social_data)
        
        # Update followers count for target user
        followers = len([
            u for u, f in social_data["follows"].items()
            if target_user in f
        ])
        
        # Update following count for current user
        following_count = len(social_data["follows"][st.session_state.username])
        
        return {
            "success": True,
            "followers": followers,
            "following": following_count
        }
        
    except Exception as e:
        st.error(f"Error toggling follow status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def toggle_like(post_id):
    """Toggle like status for a post"""
    try:
        social_data = load_social_data()
        
        # Initialize likes dictionary if it doesn't exist
        if "likes" not in social_data:
            social_data["likes"] = {}
        
        # Create unique key for this user-post combination
        like_key = f"{st.session_state.username}_{post_id}"
        
        # Find the post and update likes
        for post in social_data["posts"]:
            if post["id"] == post_id:
                # Initialize likes count if it doesn't exist
                if "likes" not in post:
                    post["likes"] = 0
                
                if like_key in social_data["likes"]:
                    # Unlike
                    post["likes"] = max(0, post["likes"] - 1)  # Ensure likes don't go below 0
                    del social_data["likes"][like_key]
                    st.toast("Post unliked", icon="💔")
                else:
                    # Like
                    post["likes"] += 1
                    social_data["likes"][like_key] = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "post_id": post_id,
                        "user_id": st.session_state.username
                    }
                    st.toast("Post liked!", icon="❤️")
                break
        
        # Save updated social data
        save_social_data(social_data)
        
        return {
            "success": True,
            "likes": post.get("likes", 0) if "post" in locals() else 0
        }
        
    except Exception as e:
        st.error(f"Error toggling like status: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

def get_post_likes(post_id):
    """Get the number of likes for a post"""
    try:
        social_data = load_social_data()
        
        # Find the post
        for post in social_data.get("posts", []):
            if post["id"] == post_id:
                return post.get("likes", 0)
        
        return 0
        
    except Exception as e:
        st.error(f"Error getting post likes: {str(e)}")
        return 0

def has_user_liked_post(post_id):
    """Check if the current user has liked a post"""
    try:
        social_data = load_social_data()
        like_key = f"{st.session_state.username}_{post_id}"
        return like_key in social_data.get("likes", {})
        
    except Exception as e:
        st.error(f"Error checking like status: {str(e)}")
        return False

def get_post_comments(post_id):
    """Get all comments for a post"""
    try:
        social_data = load_social_data()
        
        # Find the post
        for post in social_data["posts"]:
            if post["id"] == post_id:
                # Return comments list, or empty list if no comments
                return post.get("comments", [])
        
        # Return empty list if post not found
        return []
        
    except Exception as e:
        st.error(f"Error getting comments: {str(e)}")
        return []

def format_comment_date(timestamp_str):
    """Format comment timestamp into relative time"""
    try:
        comment_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        now = datetime.now()
        diff = now - comment_time
        
        if diff.days > 7:
            return comment_time.strftime("%B %d, %Y")
        elif diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds > 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds > 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    except Exception:
        return timestamp_str

def add_comment(post_id, content):
    """Add a comment to a post"""
    try:
        if not content.strip():
            st.error("Comment cannot be empty")
            return False
        
        social_data = load_social_data()
        
        # Create new comment object
        new_comment = {
            "id": str(uuid.uuid4()),
            "user_id": st.session_state.username,
            "content": content.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": 0
        }
        
        # Find the post and add the comment
        for post in social_data["posts"]:
            if post["id"] == post_id:
                # Initialize comments list if it doesn't exist
                if "comments" not in post:
                    post["comments"] = []
                
                # Add the new comment
                post["comments"].append(new_comment)
                
                # Save updated social data
                save_social_data(social_data)
                
                # Show success message
                st.toast("Comment added successfully!", icon="💬")
                return True
        
        st.error("Post not found")
        return False
        
    except Exception as e:
        st.error(f"Error adding comment: {str(e)}")
        return False

def delete_comment(post_id, comment_id):
    """Delete a comment from a post"""
    try:
        social_data = load_social_data()
        
        # Find the post
        for post in social_data["posts"]:
            if post["id"] == post_id:
                # Find and remove the comment
                # Only allow deletion if the user is the comment author
                post["comments"] = [
                    c for c in post.get("comments", [])
                    if c["id"] != comment_id or c["user_id"] != st.session_state.username
                ]
                
                # Save updated social data
                save_social_data(social_data)
                
                # Show success message
                st.toast("Comment deleted", icon="🗑️")
                return True
        
        st.error("Post not found")
        return False
        
    except Exception as e:
        st.error(f"Error deleting comment: {str(e)}")
        return False

def can_delete_comment(comment):
    """Check if current user can delete a comment"""
    return comment["user_id"] == st.session_state.username

def create_instagram_style_post(outfit, username):
    """Create an Instagram-style post layout for an outfit"""
    try:
        # Create a styled container for the post
        st.markdown("""
            <style>
            .instagram-post {
                background: white;
                border: 1px solid #dbdbdb;
                border-radius: 3px;
                margin-bottom: 20px;
                max-width: 400px;  /* Reduced from 600px */
                margin: 0 auto;
            }
            
            .post-header {
                padding: 8px;  /* Reduced from 12px */
                display: flex;
                align-items: center;
                border-bottom: 1px solid #efefef;
            }
            
            .post-header img {
                border-radius: 50%;
                margin-right: 8px;  /* Reduced from 10px */
                width: 24px;  /* Reduced from 32px */
                height: 24px;  /* Reduced from 32px */
            }
            
            .username {
                font-weight: 600;
                color: #262626;
                text-decoration: none;
                font-size: 0.9em;  /* Added smaller font size */
            }
            
            .post-content {
                width: 100%;
                background: #fafafa;
                display: flex;
                justify-content: center;
                align-items: center;
            }
            
            .outfit-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);  /* Changed to 2 columns */
                gap: 2px;  /* Reduced from 4px */
                padding: 2px;  /* Reduced from 4px */
                background: white;
            }
            
            .outfit-item {
                aspect-ratio: 1;
                object-fit: cover;
                width: 100%;
                max-width: 150px;  /* Added max-width */
                height: auto;
            }
            
            .post-actions {
                padding: 8px;  /* Reduced from 12px */
                border-top: 1px solid #efefef;
            }
            
            .post-likes {
                font-weight: 600;
                margin-bottom: 4px;  /* Reduced from 8px */
                font-size: 0.9em;
            }
            
            .post-caption {
                margin-bottom: 4px;  /* Reduced from 8px */
                font-size: 0.9em;
            }
            
            .post-comments {
                color: #8e8e8e;
                font-size: 0.8em;
            }
            
            .post-time {
                color: #8e8e8e;
                font-size: 0.7em;
                text-transform: uppercase;
            }
            
            .action-button {
                background: none;
                border: none;
                padding: 4px;  /* Reduced from 8px */
                cursor: pointer;
                color: #262626;
                font-size: 1em;  /* Reduced from 1.2em */
            }
            
            .post-engagement {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 0 8px;  /* Reduced from 12px */
            }
            
            .hashtag {
                color: #00376b;
                text-decoration: none;
                font-size: 0.8em;
            }
            
            /* Added responsive design for small screens */
            @media (max-width: 480px) {
                .instagram-post {
                    max-width: 100%;
                }
                
                .outfit-grid {
                    grid-template-columns: repeat(2, 1fr);
                }
                
                .outfit-item {
                    max-width: 120px;
                }
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Generate random engagement numbers
        likes = np.random.randint(10, 1000)
        comments = np.random.randint(1, 50)
        
        # Create hashtags (limited to 3 for more compact display)
        hashtags = [
            f"#{outfit['occasion'].replace(' ', '')}", 
            "#OOTD",
            "#StyleShare"
        ]
        
        # Create the post HTML with smaller header image
        post_html = f"""
            <div class="instagram-post">
                <div class="post-header">
                    <img src="https://api.dicebear.com/7.x/avataaars/svg?seed={username}" width="24" height="24"/>
                    <span class="username">@{username}</span>
                </div>
                
                <div class="post-content">
                    <div class="outfit-grid">
        """
        
        # Add outfit images to grid (limit to 4 items for more compact display)
        for item in outfit['items'][:4]:  # Limit to 4 items
            if os.path.exists(item['image_path']):
                try:
                    with Image.open(item['image_path']) as img:
                        # Resize image before converting to base64
                        img.thumbnail((150, 150))  # Resize to smaller dimensions
                        buffered = io.BytesIO()
                        img.save(buffered, format="JPEG", quality=85)  # Reduced quality for smaller size
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        post_html += f"""
                            <img class="outfit-item" src="data:image/jpeg;base64,{img_str}" 
                                 alt="{item['name']}" title="{item['name']}"/>
                        """
                except Exception as img_error:
                    st.warning(f"Could not process image for {item['name']}: {str(img_error)}")
                    continue
        
        # Add post actions and caption (simplified)
        post_html += f"""
                </div>
            </div>
            <div class="post-actions">
                <div class="post-engagement">
                    <div>
                        <button class="action-button">❤️</button>
                        <button class="action-button">💬</button>
                        <button class="action-button">📤</button>
                    </div>
                    <button class="action-button">🔖</button>
                </div>
                <div class="post-likes">{likes:,} likes</div>
                <div class="post-caption">
                    <span class="username">@{username}</span> 
                    {outfit['name']}<br/>
                    {' '.join(f'<a class="hashtag" href="#">{tag}</a>' for tag in hashtags)}
                </div>
                <div class="post-comments">View all {comments} comments</div>
                <div class="post-time">{(datetime.now() - timedelta(minutes=np.random.randint(1, 60))).strftime('%B %d').upper()}</div>
            </div>
        </div>
        """
        
        return st.markdown(post_html, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error creating Instagram-style post: {str(e)}")
        return None

def social_media_features():
    """Handle social media sharing and integration with Instagram-style posts"""
    st.title("📱 Social Media Integration")
    
    # Create tabs for different social features
    share_tab, connect_tab = st.tabs(["Share Outfits", "Connect Accounts"])
    
    with share_tab:
        st.markdown("### Share Your Outfits")
        
        # Load user's saved outfits
        outfit_file = f"{st.session_state.username}_outfits.json"
        if os.path.exists(outfit_file):
            with open(outfit_file, 'r') as f:
                saved_outfits = json.load(f)
            
            if saved_outfits:
                # Select outfit to share
                selected_outfit = st.selectbox(
                    "Choose an outfit to share",
                    options=[outfit['name'] for outfit in saved_outfits],
                    key="share_outfit_select"
                )
                
                # Get selected outfit details
                outfit = next((o for o in saved_outfits if o['name'] == selected_outfit), None)
                
                if outfit:
                    # Display Instagram-style post
                    create_instagram_style_post(outfit, st.session_state.username)
                    
                    # Share options
                    st.markdown("#### Share Options")
                    share_cols = st.columns(4)
                    
                    share_text = f"Check out my {outfit['name']} outfit for {outfit['occasion']}! #StyleShare #Fashion"
                    
                    with share_cols[0]:
                        if st.button("📸 Instagram"):
                            instagram_url = f"https://www.instagram.com/create/story?text={share_text}"
                            st.markdown(f"[Open Instagram]({instagram_url})")
                    
                    with share_cols[1]:
                        if st.button("🐦 Twitter"):
                            twitter_url = f"https://twitter.com/intent/tweet?text={share_text}"
                            st.markdown(f"[Open Twitter]({twitter_url})")
                    
                    with share_cols[2]:
                        if st.button("📌 Pinterest"):
                            pinterest_url = f"https://pinterest.com/pin/create/button/?description={share_text}"
                            st.markdown(f"[Open Pinterest]({pinterest_url})")
                    
                    with share_cols[3]:
                        if st.button("📋 Copy Link"):
                            share_link = f"https://yourapp.com/outfit/{outfit['id']}"
                            pyperclip.copy(share_link)
                            st.success("Link copied!")
            else:
                st.info("No outfits saved yet! Create some outfits to share.")
        else:
            st.info("No outfits saved yet! Create some outfits to share.")
    
    with connect_tab:
        st.markdown("### Connect Your Social Accounts")
        
        # Load existing connections
        profile_file = f"{st.session_state.username}_profile.json"
        social_connections = {}
        
        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
                social_connections = profile_data.get('social_connections', {})
        
        # Social media connection form
        with st.form("social_connect_form"):
            instagram_handle = st.text_input(
                "Instagram Handle",
                value=social_connections.get('instagram', ''),
                placeholder="@username"
            )
            
            pinterest_username = st.text_input(
                "Pinterest Username",
                value=social_connections.get('pinterest', ''),
                placeholder="username"
            )
            
            twitter_handle = st.text_input(
                "Twitter Handle",
                value=social_connections.get('twitter', ''),
                placeholder="@username"
            )
            
            if st.form_submit_button("Save Connections"):
                try:
                    # Update social connections
                    social_connections = {
                        'instagram': instagram_handle,
                        'pinterest': pinterest_username,
                        'twitter': twitter_handle
                    }
                    
                    # Save to profile
                    if os.path.exists(profile_file):
                        with open(profile_file, 'r') as f:
                            profile_data = json.load(f)
                    else:
                        profile_data = {}
                    
                    profile_data['social_connections'] = social_connections
                    
                    with open(profile_file, 'w') as f:
                        json.dump(profile_data, f, indent=2)
                    
                    st.success("Social connections updated!")
                except Exception as e:
                    st.error(f"Error saving social connections: {str(e)}")

# Main function
def main():
    """Main function to run the Streamlit app"""
    # Initialize session state for style quiz if not exists
    if 'show_style_quiz' not in st.session_state:
        st.session_state.show_style_quiz = False
        
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False
    
    # Initialize session state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None

    # Sidebar navigation
    if st.session_state.logged_in:
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Home", "Image Uploader and Display", "Saved Clothes", 
             "Clothing Data Insights with GPT-4", "Weather-Based Outfits", 
             "Saved Outfits", "Outfit Calendar", "Style Quizzes", 
             # "Shopping Recommendations", 
             "Trading Marketplace"]
        )
    else:
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Home", "Login/Register"]
        )
    
    # Display the selected page
    if page == "Home":
        homepage()
    elif page == "Login/Register":
        if not st.session_state.logged_in:
            tab1, tab2 = st.tabs(["Login", "Create Account"])
            with tab1:
                login()
            with tab2:
                create_account()
        else:
            st.title(f"Welcome back, {st.session_state.username}!")
    elif page == "Image Uploader and Display":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            image_uploader_and_display()
    elif page == "Saved Clothes":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            display_saved_clothes()
    elif page == "Clothing Data Insights with GPT-4":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            clothing_data_insights()
    elif page == "Weather-Based Outfits":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            weather_based_outfits()
    elif page == "Saved Outfits":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            display_saved_outfits()
    elif page == "Outfit Calendar":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            schedule_outfits()
    elif page == "Style Quizzes":
        if not st.session_state.logged_in:
            st.warning("Please log in to access this feature.")
            login()
        else:
            style_quizzes()
    # elif page == "Shopping Recommendations":
    #     shopping_recommendations()
    elif page == "Trading Marketplace":
        if not st.session_state.logged_in:
            st.warning("Please log in to access the Trading Marketplace.")
            login()
        else:
            trading_marketplace()

    # In your main app flow, after authentication
    if "logged_in" in st.session_state and st.session_state.logged_in:
        # Add this line to your existing sidebar content
        st.sidebar.markdown("---")  # Adds a separator line
        add_social_features()  # Adds the social features section

# At the bottom of your file
if __name__ == "__main__":
    main()