"""Clothing manager module for handling wardrobe operations"""

import streamlit as st
import pandas as pd
import os
from PIL import Image
<<<<<<< HEAD
import json
from datetime import datetime

def load_user_clothing():
    """Load user's clothing items from CSV"""
    if "username" not in st.session_state:
        return pd.DataFrame()
        
    clothing_file = f"{st.session_state.username}_clothing.csv"
    if os.path.exists(clothing_file):
        return pd.read_csv(clothing_file)
    return pd.DataFrame(columns=[
        'name', 'type_of_clothing', 'color', 'season', 
        'occasion', 'image_path', 'additional_details'
    ])

def save_user_clothing(df):
    """Save user's clothing items to CSV"""
    if "username" not in st.session_state:
        return False
        
    clothing_file = f"{st.session_state.username}_clothing.csv"
    try:
        df.to_csv(clothing_file, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving clothing data: {str(e)}")
        return False

def check_duplicate_name(name: str, user_clothing: pd.DataFrame) -> bool:
    """Check if a clothing item name already exists"""
    return name.lower() in user_clothing['name'].str.lower().values

def suggest_unique_name(base_name: str, user_clothing: pd.DataFrame) -> str:
    """Suggest a unique name for a clothing item"""
    counter = 1
    new_name = base_name
    while check_duplicate_name(new_name, user_clothing):
        counter += 1
        new_name = f"{base_name} {counter}"
    return new_name 
=======
import uuid
import openai
from pydantic import BaseModel
import plotly.express as px

# Clothing Item Response Model
class ClothingItemResponse(BaseModel):
    name: str
    color: str
    type_of_clothing: str
    season: str
    occasion: str
    additional_details: str = ""

def gpt4o_structured_clothing(item_description: str):
    """Get GPT-4 analysis of clothing item"""
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
    
    Focus on creating a concise, professional name that would appear in a luxury store catalog."""

    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": item_description}
            ]
        )
        
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

def load_user_clothing():
    """Load user's clothing data from CSV"""
    user_file = f"{st.session_state.username}_clothing.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    else:
        return pd.DataFrame(columns=["id", "name", "color", "type_of_clothing", "season", "occasion", "image_path"])

def save_user_clothing(df):
    """Save user's clothing data to CSV"""
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
    """Handle image upload and clothing item creation"""
    st.title("Add to Your Wardrobe")
    
    save_directory = "uploads"
    if not os.path.exists(save_directory):
        try:
            os.makedirs(save_directory)
        except Exception as e:
            st.error(f"Could not create uploads directory: {e}")
            return

    uploaded_files = st.file_uploader(
        "Choose an image file", 
        accept_multiple_files=True, 
        type=["jpg", "jpeg", "png", "webp"]
    )

    if uploaded_files:
        st.markdown("<h3 style='color: #2c3e50;'>New Items</h3>", unsafe_allow_html=True)
        user_clothing = load_user_clothing()
        
        for uploaded_file in uploaded_files:
            process_uploaded_file(uploaded_file, user_clothing, save_directory)

def process_uploaded_file(uploaded_file, user_clothing, save_directory):
    """Process a single uploaded file"""
    try:
        image = Image.open(uploaded_file)
        st.image(image, caption=uploaded_file.name, width=150)

        image_path = os.path.join(save_directory, uploaded_file.name)
        image.save(image_path)

        description = f"Please analyze this clothing item in detail: {uploaded_file.name}"
        clothing_description = gpt4o_structured_clothing(description)
        suggested_name = suggest_unique_name(clothing_description.name, user_clothing)

        display_clothing_form(suggested_name, clothing_description, image_path, user_clothing)

    except Exception as e:
        st.error(f"Error processing {uploaded_file.name}: {str(e)}")

def display_clothing_form(suggested_name, clothing_description, image_path, user_clothing):
    """Display and handle the clothing item form"""
    with st.container():
        st.markdown("<div style='background-color: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px;'>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style='margin-bottom: 15px;'>
                <strong>AI-Suggested Name:</strong> {suggested_name}
            </div>
        """, unsafe_allow_html=True)
        
        name = st.text_input(
            "Item Name (Edit if needed)",
            value=suggested_name,
            help="You can keep the AI-suggested name or create your own. Names must be unique.",
            key=f"name_input_{image_path}"
        )

        # Form fields
        color_options = ["Red", "Blue", "Green", "Yellow", "Black", "White", 
                        "Purple", "Orange", "Pink", "Brown", "Gray", "Multi-color"]
        colors = st.multiselect(
            "Colors",
            options=color_options,
            default=[clothing_description.color] if clothing_description.color in color_options else [],
            key=f"colors_multiselect_{image_path}"
        )

        type_options = ["Shirt", "Pants", "Jacket", "Dress", "Skirt", "Shorts", 
                       "Sweater", "T-shirt", "Blouse", "Coat", "Jeans", "Shoes"]
        type_of_clothing = st.selectbox(
            "Type of Clothing",
            options=type_options,
            index=type_options.index(clothing_description.type_of_clothing) 
                  if clothing_description.type_of_clothing in type_options else 0,
            key=f"type_selectbox_{image_path}"
        )

        season_options = ["Spring", "Summer", "Fall", "Winter", "All Seasons"]
        seasons = st.multiselect(
            "Suitable Seasons",
            options=season_options,
            default=[clothing_description.season] if clothing_description.season in season_options else [],
            key=f"seasons_multiselect_{image_path}"
        )

        occasion_options = ["Casual", "Formal", "Business", "Party", "Sports", 
                          "Outdoor", "Beach", "Wedding", "Everyday"]
        occasions = st.multiselect(
            "Appropriate Occasions",
            options=occasion_options,
            default=[clothing_description.occasion] if clothing_description.occasion in occasion_options else [],
            key=f"occasions_multiselect_{image_path}"
        )

        additional_details = st.text_area(
            "Additional Details",
            value=clothing_description.additional_details,
            key=f"additional_details_{image_path}"
        )

        save_clothing_item(name, colors, type_of_clothing, seasons, occasions, 
                         additional_details, image_path, user_clothing)

def save_clothing_item(name, colors, type_of_clothing, seasons, occasions, 
                      additional_details, image_path, user_clothing):
    """Save a clothing item to the database"""
    if st.button("Save", key=f"save_button_{image_path}"):
        if check_duplicate_name(name, user_clothing):
            st.error(f"An item with the name '{name}' already exists. Please choose a different name.")
            return

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
        
        user_clothing = pd.concat([user_clothing, new_data], ignore_index=True)
        save_user_clothing(user_clothing)
        st.success(f"'{name}' saved successfully!")

def display_saved_clothes():
    """Display saved clothes with filtering options"""
    st.title("👚 Saved Clothes")
    user_clothing = load_user_clothing()

    if user_clothing.empty:
        st.write("No clothes saved yet!")
        return

    # Filter options
    clothing_type_options = ["Shirt", "Pants", "Jacket", "Dress", "Skirt", "Shorts", 
                           "Sweater", "T-shirt", "Blouse", "Coat", "Jeans", "Shoes"]
    color_options = ["Red", "Blue", "Green", "Yellow", "Black", "White", 
                    "Purple", "Orange", "Pink", "Brown", "Gray", "Multi-color"]
    season_options = ["Spring", "Summer", "Fall", "Winter", "All Seasons"]
    occasion_options = ["Casual", "Formal", "Business", "Party", "Sports", 
                       "Outdoor", "Beach", "Wedding", "Everyday"]

    # Filter selections
    selected_clothing_types = st.multiselect("Select Clothing Types to Filter", clothing_type_options)
    selected_colors = st.multiselect("Select Colors to Filter", color_options)
    selected_seasons = st.multiselect("Select Seasons to Filter", season_options)
    selected_occasions = st.multiselect("Select Occasions to Filter", occasion_options)

    if st.button("Filter Clothes"):
        display_filtered_clothes(user_clothing, selected_clothing_types, 
                               selected_colors, selected_seasons, selected_occasions)

def display_filtered_clothes(user_clothing, selected_types, selected_colors, 
                           selected_seasons, selected_occasions):
    """Display filtered clothing items"""
    if not user_clothing.empty:
        filtered_clothes = user_clothing

        if selected_types:
            filtered_clothes = filtered_clothes[filtered_clothes['type_of_clothing'].isin(selected_types)]
        if selected_colors:
            filtered_clothes = filtered_clothes[filtered_clothes['color'].isin(selected_colors)]
        if selected_seasons:
            filtered_clothes = filtered_clothes[filtered_clothes['season'].isin(selected_seasons)]
        if selected_occasions:
            filtered_clothes = filtered_clothes[filtered_clothes['occasion'].isin(selected_occasions)]

        display_clothes_grid(filtered_clothes)

def display_clothes_grid(filtered_clothes):
    """Display clothes in a grid layout"""
    clothes_per_row = 3
    for i in range(0, len(filtered_clothes), clothes_per_row):
        cols = st.columns(clothes_per_row)
        for idx, item in enumerate(filtered_clothes.iloc[i:i + clothes_per_row].to_dict(orient='records')):
            with cols[idx]:
                display_clothing_item(item)

def display_clothing_item(item):
    """Display a single clothing item"""
    try:
        image_path = item['image_path']
        if not os.path.exists(image_path):
            new_path = os.path.join('uploads', os.path.basename(image_path))
            if os.path.exists(new_path):
                image_path = new_path
                update_image_path(item['id'], new_path)
        
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
        
        if item.get('additional_details'):
            st.markdown(f"""
                <div style='margin-top: 10px; padding: 10px; border-left: 3px solid #2c3e50;'>
                    <strong>Details:</strong><br>
                    {item['additional_details']}
                </div>
            """, unsafe_allow_html=True)
        
        handle_delete_item(item)
        st.write("---")
    except Exception as e:
        st.error(f"Error displaying {item['name']}: {str(e)}")

def handle_delete_item(item):
    """Handle deletion of a clothing item"""
    unique_key = f"delete_{item['id']}"
    if st.button(f"Delete {item['name']}", key=unique_key):
        delete_clothing_item(item)

def delete_clothing_item(item):
    """Delete a clothing item and its image"""
    try:
        if os.path.exists(item['image_path']):
            os.remove(item['image_path'])
    except Exception as e:
        st.warning(f"Could not delete image file: {e}")

    user_clothing = load_user_clothing()
    user_clothing = user_clothing[user_clothing['id'] != item['id']]
    save_user_clothing(user_clothing)
    st.success(f"{item['name']} deleted successfully.")
    st.rerun()

def update_image_path(item_id, new_path):
    """Update the image path in the database"""
    user_clothing = load_user_clothing()
    user_clothing.loc[user_clothing['id'] == item_id, 'image_path'] = new_path
    save_user_clothing(user_clothing)

def clothing_data_insights():
    """Display insights and analytics about the user's wardrobe"""
    st.title("👕 Wardrobe Analytics")
    
    try:
        # Load user's clothing data
        df = pd.read_csv(f"{st.session_state.username}_clothing.csv")
        
        if len(df) == 0:
            st.info("Add some clothes to your wardrobe to see insights!")
            return
            
        # Display total items
        st.subheader("Wardrobe Overview")
        total_items = len(df)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Items", total_items)
        with col2:
            st.metric("Unique Categories", df['type_of_clothing'].nunique())
        with col3:
            st.metric("Total Value", f"${df['price'].sum():.2f}")
            
        # Clothing categories breakdown
        st.subheader("Clothing Categories")
        category_counts = df['type_of_clothing'].value_counts()
        fig = px.pie(values=category_counts.values, 
                    names=category_counts.index,
                    title='Distribution of Clothing Types')
        st.plotly_chart(fig)
        
        # Color analysis
        st.subheader("Color Analysis")
        color_counts = df['color'].value_counts()
        fig = px.bar(x=color_counts.index, 
                    y=color_counts.values,
                    title='Color Distribution in Your Wardrobe',
                    labels={'x': 'Color', 'y': 'Count'})
        st.plotly_chart(fig)
        
        # Season distribution
        st.subheader("Seasonal Distribution")
        season_counts = df['season'].str.split(',').explode().str.strip().value_counts()
        fig = px.bar(x=season_counts.index, 
                    y=season_counts.values,
                    title='Seasonal Distribution of Clothes',
                    labels={'x': 'Season', 'y': 'Count'})
        st.plotly_chart(fig)
        
        # Price analysis
        st.subheader("Price Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.box(df, y='price', title='Price Distribution')
            st.plotly_chart(fig)
        with col2:
            avg_price_by_category = df.groupby('type_of_clothing')['price'].mean().sort_values(ascending=False)
            fig = px.bar(x=avg_price_by_category.index, 
                        y=avg_price_by_category.values,
                        title='Average Price by Category',
                        labels={'x': 'Category', 'y': 'Average Price ($)'})
            st.plotly_chart(fig)
            
        # Most and least expensive items
        st.subheader("Price Insights")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Most Expensive Items:")
            most_expensive = df.nlargest(5, 'price')[['name', 'type_of_clothing', 'price']]
            st.dataframe(most_expensive)
        with col2:
            st.write("Most Affordable Items:")
            least_expensive = df.nsmallest(5, 'price')[['name', 'type_of_clothing', 'price']]
            st.dataframe(least_expensive)
            
        # Style analysis
        if 'style' in df.columns:
            st.subheader("Style Analysis")
            style_counts = df['style'].value_counts()
            fig = px.pie(values=style_counts.values, 
                        names=style_counts.index,
                        title='Distribution of Style Categories')
            st.plotly_chart(fig)
            
        # Wardrobe gaps analysis
        st.subheader("Wardrobe Gaps Analysis")
        
        # Check seasonal balance
        season_balance = season_counts.to_dict()
        seasons = ['Spring', 'Summer', 'Fall', 'Winter']
        missing_seasons = [s for s in seasons if s not in season_balance or season_balance[s] < 5]
        
        # Check basic essentials
        essential_categories = {
            'Tops': ['T-shirt', 'Blouse', 'Shirt'],
            'Bottoms': ['Pants', 'Jeans', 'Skirt'],
            'Outerwear': ['Jacket', 'Coat'],
            'Dresses': ['Dress'],
            'Shoes': ['Sneakers', 'Boots', 'Flats']
        }
        
        missing_essentials = []
        for category, items in essential_categories.items():
            category_items = df[df['type_of_clothing'].isin(items)]
            if len(category_items) < 2:
                missing_essentials.append(category)
        
        # Display recommendations
        st.write("#### Wardrobe Recommendations")
        
        if missing_seasons:
            st.write("Consider adding more items for these seasons:")
            for season in missing_seasons:
                st.write(f"- {season}")
                
        if missing_essentials:
            st.write("Consider adding these essential categories:")
            for category in missing_essentials:
                st.write(f"- {category}")
                
        # Display versatility score
        versatility_score = calculate_versatility_score(df)
        st.metric("Wardrobe Versatility Score", f"{versatility_score}/100")
        
    except FileNotFoundError:
        st.info("Add some clothes to your wardrobe to see insights!")
    except Exception as e:
        st.error(f"Error analyzing wardrobe data: {str(e)}")

def calculate_versatility_score(df):
    """Calculate a versatility score for the wardrobe"""
    score = 0
    
    # Basic categories coverage (30 points)
    essential_categories = ['Tops', 'Bottoms', 'Dresses', 'Outerwear', 'Shoes']
    categories_present = df['type_of_clothing'].unique()
    score += (len(set(categories_present) & set(essential_categories)) / len(essential_categories)) * 30
    
    # Seasonal balance (30 points)
    seasons = df['season'].str.split(',').explode().str.strip().value_counts()
    season_balance = 30 - (seasons.std() / seasons.mean() * 10 if len(seasons) > 0 else 30)
    score += max(0, season_balance)
    
    # Color variety (20 points)
    color_count = df['color'].nunique()
    score += min(20, (color_count / 10) * 20)
    
    # Price efficiency (10 points)
    if 'price' in df.columns:
        price_range = df['price'].max() - df['price'].min()
        price_score = 10 - (price_range / df['price'].mean() / 2)
        score += max(0, price_score)
    
    # Style variety (10 points)
    if 'style' in df.columns:
        style_count = df['style'].nunique()
        score += min(10, (style_count / 5) * 10)
    
    return round(score) 
>>>>>>> 82784ae66500dcd327bb26ca80802df0894371fb
