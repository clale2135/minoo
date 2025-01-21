import streamlit as st
import pandas as pd
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