import streamlit as st
import json
from datetime import datetime
import os
from PIL import Image

def load_saved_outfits():
    outfit_file = f"{st.session_state.username}_outfits.json"
    try:
        if os.path.exists(outfit_file):
            with open(outfit_file, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        st.error(f"Error loading outfits: {str(e)}")
        return []

def display_saved_outfits():
    st.title("📱 Saved Outfits")
    # ... rest of the function code ...

def schedule_outfits():
    st.title("📅 Outfit Calendar")
    # ... rest of the function code ... 