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
import time


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)
USER_DB_PATH = "users.csv"


def set_custom_style():
    st.markdown("""
        <style>
        /* Hide the default white background */
        .stApp {
            background-color: transparent;
        }
        
        /* Main container styling */
        .main {
            padding: 2rem;
        }
        
        /* Header styling */
        .stTitle {
            color: #2c3e50;
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 500;
            padding-bottom: 1.5rem;
        }
        
        /* Button styling */
        .stButton > button {
            background-color: #2c3e50;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #34495e;
            transform: translateY(-2px);
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #f8f9fa;
        }
        
        /* Card-like containers for clothes */
        .clothes-card {
            background-color: white;
            border-radius: 10px;
            padding: 1rem;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: all 0.3s ease;
        }
        
        .clothes-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Image styling */
        .stImage {
            border-radius: 8px;
            overflow: hidden;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input {
            border-radius: 5px;
            border: 1px solid #e0e0e0;
        }
        
        /* Multiselect styling */
        .stMultiSelect > div > div > div {
            border-radius: 5px;
        }
        
        /* Success message styling */
        .stSuccess {
            background-color: #d4edda;
            color: #155724;
            padding: 0.75rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        
        /* Error message styling */
        .stError {
            background-color: #f8d7da;
            color: #721c24;
            padding: 0.75rem;
            border-radius: 5px;
            margin: 1rem 0;
        }

        /* Remove white background from markdown */
        .element-container {
            background-color: transparent !important;
        }
        
        /* Remove white background from dataframe */
        .stDataFrame {
            background-color: transparent !important;
        }

        /* Style welcome message without background */
        .welcome-msg {
            color: #2c3e50;
            text-align: center;
            padding: 1rem 0;
            margin-bottom: 2rem;
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
            st.toast("Username already exists.", icon="⚠️")
        else:
            add_user(username, password)
            st.toast("Account created successfully!", icon="✅")


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
    prompt = """You are an expert in fashion. Please describe the following clothing item in detail. 
    Return your response in this exact format:
    {
        "name": "Brief descriptive name",
        "color": "Primary color",
        "type_of_clothing": "Category",
        "season": "Primary season",
        "occasion": "Primary occasion",
        "additional_details": "Include any notable features such as: patterns, prints, logos, signature designs, material type, unique characteristics, brand-specific details, or special care instructions"
    }
    
    For each item, analyze:
    1. A descriptive name for the piece
    2. Primary colors present
    3. Type of clothing (e.g., shirt, pants, dress)
    4. Suitable seasons (consider fabric weight, style, and color)
    5. Appropriate occasions
    6. Any distinctive features, patterns, or designs
    
    Be specific about:
    - Seasons: Spring, Summer, Fall, Winter, or All Seasons
    - Occasions: Casual, Formal, Business, Party, Sports, Outdoor, Beach, Wedding, Everyday
    - Additional details should capture unique characteristics that make this item special"""

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


def clothing_data_insights():
    st.title("Clothing Data Insights with GPT-4")
    user_clothing = load_user_clothing()

    if user_clothing.empty:
        st.write("No clothing data available for insights.")
        return

    st.write("Here is a preview of your saved clothing data:")
    st.dataframe(user_clothing)
    user_question = st.text_input("Enter your question based on the clothing data:")

    if st.button("Get Insights"):
        if user_question.strip() == "":
            st.error("Please enter a question.")
        else:
            prompt = f"Here is some clothing data:\n{user_clothing.to_string(index=False)}\n------\nAnswer the following questions:\n{user_question}"
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Imagine you are an expert fashion analyst. With a basic overview, even if the clothes don't fit the prompt, answer this:"},
                    {"role": "user", "content": prompt}
                ]
            )
            st.write("### GPT-4's Insight:")
            st.write(response.choices[0].message.content.strip())


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


def load_user_outfits():
    """Load saved outfits for the current user"""
    try:
        outfit_file = f"{st.session_state.username}_outfits.csv"
        if not os.path.exists(outfit_file):
            df = pd.DataFrame(columns=["id", "outfit_name", "items", "style_description", "occasion", "styling_tips"])
            df.to_csv(outfit_file, index=False)  # Create the file if it doesn't exist
        return pd.read_csv(outfit_file)
    except Exception as e:
        st.error(f"Error loading outfits: {str(e)}")
        return pd.DataFrame(columns=["id", "outfit_name", "items", "style_description", "occasion", "styling_tips"])


def save_user_outfits(outfits_df):
    """Save outfits for the current user"""
    try:
        outfit_file = f"{st.session_state.username}_outfits.csv"
        outfits_df.to_csv(outfit_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving outfits: {str(e)}")
        return False


def create_outfit():
    st.title("Create an Outfit")
    user_clothing = load_user_clothing()

    if user_clothing.empty:
        st.write("No clothes saved yet! Add some clothes first.")
        return

    # Get outfit suggestion from GPT-4
    if st.button("Generate New Outfit"):
        # Create a detailed prompt with all available clothing items
        clothing_list = user_clothing.apply(
            lambda x: f"- {x['name']}: {x['type_of_clothing']} ({x['color']}, suitable for {x['season']}, {x['occasion']})", 
            axis=1
        ).tolist()
        
        prompt = f"""As a fashion expert, create a stylish outfit using ONLY the following available clothes:

{chr(10).join(clothing_list)}

IMPORTANT: Only use exact names from the list above. Do not suggest any items that are not in the list.

Return your response in this exact format:
{{
    "outfit_name": "Name of the outfit combination",
    "items": ["item_name1", "item_name2", "item_name3"],
    "style_description": "Brief description of the style",
    "occasion": "Suggested occasion",
    "styling_tips": "Additional styling tips"
}}

Choose 2-4 items that work well together considering colors, style, and occasion."""

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a fashion expert creating outfits. Only use items from the provided list."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            import json
            outfit_data = json.loads(response.choices[0].message.content)
            
            # Validate that all suggested items exist in the wardrobe
            valid_items = []
            invalid_items = []
            
            for item_name in outfit_data['items']:
                matching_items = user_clothing[user_clothing['name'].str.lower() == item_name.lower()]
                if not matching_items.empty:
                    valid_items.append(matching_items.iloc[0])
                else:
                    invalid_items.append(item_name)
            
            if invalid_items:
                st.warning(f"Some suggested items were not found in your wardrobe: {', '.join(invalid_items)}")
                st.write("Showing outfit with available items only.")
            
            if not valid_items:
                st.error("None of the suggested items were found in your wardrobe. Please try generating again.")
                return

            # Display the outfit
            st.markdown(f"""
                <h2 style='color: #2c3e50; margin-bottom: 20px;'>{outfit_data['outfit_name']}</h2>
            """, unsafe_allow_html=True)

            # Create columns for the valid outfit items
            num_items = len(valid_items)
            cols = st.columns(num_items)

            # Display each valid item in the outfit with its image
            for idx, item in enumerate(valid_items):
                with cols[idx]:
                    try:
                        # Display the image
                        if os.path.exists(item['image_path']):
                            with open(item['image_path'], 'rb') as file:
                                image_bytes = file.read()
                            st.image(image_bytes, caption=item['name'], width=150)
                        else:
                            st.warning(f"Image not found for {item['name']}")
                        
                        # Display item details
                        st.markdown(f"""
                            <div style='text-align: center;'>
                                <strong>{item['name']}</strong><br>
                                {item['type_of_clothing']}<br>
                                <em>{item['color']}</em>
                            </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error displaying {item['name']}: {str(e)}")

            # After displaying the outfit and styling information
            st.markdown("""
                <div style='margin-top: 30px; padding: 20px; background-color: rgba(44, 62, 80, 0.1); border-radius: 10px;'>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <h3 style='color: #2c3e50;'>Style Details</h3>
                <p><strong>Description:</strong> {outfit_data['style_description']}</p>
                <p><strong>Perfect for:</strong> {outfit_data['occasion']}</p>
                <p><strong>Styling Tips:</strong> {outfit_data['styling_tips']}</p>
            """, unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

            # Save outfit section
            st.markdown("<div style='margin-top: 30px;'>", unsafe_allow_html=True)
            outfit_name = st.text_input(
                "Name this outfit",
                value=outfit_data['outfit_name'],
                key="outfit_name_input"
            )

            if st.button("💾 Save Outfit"):
                if not outfit_name:
                    st.error("Please provide a name for the outfit.")
                    return

                try:
                    # Load existing outfits
                    outfits_file = f"{st.session_state.username}_outfits.csv"
                    
                    if os.path.exists(outfits_file):
                        user_outfits = pd.read_csv(outfits_file)
                    else:
                        user_outfits = pd.DataFrame(columns=[
                            "id", "outfit_name", "items", "style_description", 
                            "occasion", "styling_tips"
                        ])

                    # Check for duplicate names
                    if outfit_name in user_outfits['outfit_name'].values:
                        st.error("An outfit with this name already exists. Please choose a different name.")
                        return

                    # Create new outfit entry
                    new_outfit = pd.DataFrame([{
                        "id": str(uuid.uuid4()),
                        "outfit_name": outfit_name,
                        "items": json.dumps([item['name'] for item in valid_items]),
                        "style_description": outfit_data['style_description'],
                        "occasion": outfit_data['occasion'],
                        "styling_tips": outfit_data['styling_tips']
                    }])

                    # Append new outfit and save
                    user_outfits = pd.concat([user_outfits, new_outfit], ignore_index=True)
                    user_outfits.to_csv(outfits_file, index=False)
                    
                    # Show success message with navigation instructions
                    st.success(f"""
                        Outfit '{outfit_name}' saved successfully! 
                        You can view it in the 'Saved Outfits' page.
                    """)
                    
                    # Add a button to view saved outfits
                    if st.button("👉 Go to Saved Outfits"):
                        # Set the page to Saved Outfits
                        st.session_state.page = "Saved Outfits"
                        st.rerun()
                        
                except Exception as e:
                    st.error(f"Error saving outfit: {str(e)}")

        except Exception as e:
            st.error(f"Error creating outfit: {str(e)}")
            st.write("Please try generating again.")


def view_saved_outfits():
    st.title("Your Saved Outfits")
    
    # Load outfits
    outfits_file = f"{st.session_state.username}_outfits.csv"
    
    if not os.path.exists(outfits_file):
        st.info("No outfits saved yet! Go to 'Create Outfit' to make your first outfit.")
        return
        
    try:
        user_outfits = pd.read_csv(outfits_file)
        if user_outfits.empty:
            st.info("No outfits saved yet! Go to 'Create Outfit' to make your first outfit.")
            return
            
        # Debug information
        st.write(f"Found {len(user_outfits)} saved outfits")
        
        # Load clothing data
        user_clothing = load_user_clothing()
        
        # Add filters for occasions
        occasions = sorted(user_outfits['occasion'].unique())
        selected_occasion = st.selectbox("Filter by occasion", ["All"] + list(occasions))
        
        filtered_outfits = user_outfits
        if selected_occasion != "All":
            filtered_outfits = user_outfits[user_outfits['occasion'] == selected_occasion]

        # Display outfits
        for _, outfit in filtered_outfits.iterrows():
            with st.container():
                st.markdown(f"""
                    <div style='padding: 20px; background-color: rgba(44, 62, 80, 0.1); 
                         border-radius: 10px; margin-bottom: 20px;'>
                    <h2 style='color: #2c3e50; margin-bottom: 10px;'>{outfit['outfit_name']}</h2>
                    <p><em>Perfect for: {outfit['occasion']}</em></p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display items
                try:
                    items = json.loads(outfit['items'])
                    cols = st.columns(len(items))
                    
                    for idx, item_name in enumerate(items):
                        with cols[idx]:
                            item_data = user_clothing[user_clothing['name'] == item_name]
                            if not item_data.empty:
                                item = item_data.iloc[0]
                                if os.path.exists(item['image_path']):
                                    with open(item['image_path'], 'rb') as file:
                                        st.image(file.read(), caption=item['name'], width=150)
                                else:
                                    st.warning(f"Image not found for {item['name']}")
                                
                                st.markdown(f"""
                                    <div style='text-align: center;'>
                                        <strong>{item['name']}</strong><br>
                                        {item['type_of_clothing']}<br>
                                        <em>{item['color']}</em>
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.warning(f"Item '{item_name}' not found in your wardrobe")
                except Exception as e:
                    st.error(f"Error displaying outfit items: {str(e)}")
                
                # Style details
                st.markdown(f"""
                    <div style='margin-top: 20px;'>
                        <h4 style='color: #2c3e50;'>Style Details</h4>
                        <p><strong>Description:</strong> {outfit['style_description']}</p>
                        <p><strong>Styling Tips:</strong> {outfit['styling_tips']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                # Delete button
                if st.button("🗑️ Delete Outfit", key=f"delete_{outfit['id']}"):
                    user_outfits = user_outfits[user_outfits['id'] != outfit['id']]
                    user_outfits.to_csv(outfits_file, index=False)
                    st.success("Outfit deleted successfully!")
                    time.sleep(1)
                    st.rerun()
                
                st.markdown("<hr>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error loading saved outfits: {str(e)}")
        st.write("Error details:", str(e))


# Main function
def main():
    set_custom_style()
    
    # Initialize session state variables
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "logout_clicked" not in st.session_state:
        st.session_state.logout_clicked = False
    if "page" not in st.session_state:
        st.session_state.page = "Image Uploader and Display"

    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50; padding: 2rem 0;'>
            👔 Your Digital Wardrobe
        </h1>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in and st.session_state.username:
        migrate_images()
        st.markdown(f"""
            <div class='welcome-msg'>
                Welcome back, <strong>{st.session_state.username}</strong>! 
                Let's organize your wardrobe today.
            </div>
        """, unsafe_allow_html=True)

        # Use session state for page selection
        st.session_state.page = st.sidebar.selectbox(
            "Choose a page",
            ["Image Uploader and Display", "Saved Clothes", "Create Outfit", 
             "Saved Outfits", "Clothing Data Insights with GPT-4"],
            index=["Image Uploader and Display", "Saved Clothes", "Create Outfit", 
                   "Saved Outfits", "Clothing Data Insights with GPT-4"].index(st.session_state.page)
        )
        
        logout()
        
        if st.session_state.page == "Image Uploader and Display":
            image_uploader_and_display()
        elif st.session_state.page == "Saved Clothes":
            display_saved_clothes()
        elif st.session_state.page == "Create Outfit":
            create_outfit()
        elif st.session_state.page == "Saved Outfits":
            view_saved_outfits()
        elif st.session_state.page == "Clothing Data Insights with GPT-4":
            clothing_data_insights()
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