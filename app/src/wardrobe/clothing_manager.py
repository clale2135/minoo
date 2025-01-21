"""Clothing manager module for handling wardrobe operations"""

import streamlit as st
import pandas as pd
import os
from PIL import Image
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