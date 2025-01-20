import streamlit as st
import pandas as pd
import os
from PIL import Image
import uuid
from ..utils.gpt_helpers import gpt4o_structured_clothing

def load_user_clothing():
    user_file = f"{st.session_state.username}_clothing.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    else:
        return pd.DataFrame(columns=["id", "name", "color", "type_of_clothing", "season", "occasion", "image_path"])

def save_user_clothing(df):
    user_file = f"{st.session_state.username}_clothing.csv"
    df.to_csv(user_file, index=False)

def image_uploader_and_display():
    st.title("Add to Your Wardrobe")
    # ... rest of the function code ...

def display_saved_clothes():
    st.title("👚 Saved Clothes")
    # ... rest of the function code ...

def clothing_data_insights():
    st.title("Clothing Data Insights with GPT-4")
    # ... rest of the function code ... 