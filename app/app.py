import streamlit as st
from src.auth.auth_handlers import login, create_account
from src.wardrobe.clothing_manager import (
    image_uploader_and_display,
    display_saved_clothes,
    clothing_data_insights
)
from src.wardrobe.outfit_manager import (
    display_saved_outfits,
    schedule_outfits
)
from src.weather.weather_service import display_weather_outfit_recommendations
from src.quizzes.style_quiz import style_quizzes, show_tutorial
from src.styles.custom_styles import set_custom_style
from dotenv import load_dotenv
import os

# Set page config first, before any other Streamlit commands
st.set_page_config(
    page_title="Digital Wardrobe",
    page_icon="👔",
    layout="wide"
)

# Load environment variables
load_dotenv()

def initialize_session_state():
    """Initialize session state variables"""
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "show_style_quiz" not in st.session_state:
        st.session_state.show_style_quiz = False

def show_welcome_message():
    """Display welcome message for logged out users"""
    st.markdown("""
        <div class='welcome-msg'>
            Welcome to Your Digital Wardrobe!
            <br>Please login or create an account to get started.
        </div>
    """, unsafe_allow_html=True)

def handle_authentication():
    """Handle user authentication"""
    auth_page = st.sidebar.selectbox("Authentication", ["Login", "Create Account"])
    if auth_page == "Login":
        login()
    else:
        create_account()

def show_navigation():
    """Display navigation sidebar for logged-in users"""
    pages = {
        "Home": homepage,
        "Add Clothes": image_uploader_and_display,
        "View Wardrobe": display_saved_clothes,
        "Outfit Suggestions": clothing_data_insights,
        "Weather Outfits": display_weather_outfit_recommendations,
        "Saved Outfits": display_saved_outfits,
        "Calendar": schedule_outfits,
        "Style Quiz": style_quizzes
    }
    
    current_page = st.query_params.get("page", "Home")
    selected_page = st.sidebar.selectbox(
        "Navigation",
        list(pages.keys()),
        index=list(pages.keys()).index(current_page)
    )
    
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()
    
    return pages[selected_page]

def homepage():
    """Display the homepage dashboard"""
    st.title(f"Welcome, {st.session_state.username}! 👋")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Quick Actions")
        if st.button("➕ Add New Clothes"):
            st.query_params["page"] = "Add Clothes"
            st.rerun()
        if st.button("👔 View Wardrobe"):
            st.query_params["page"] = "View Wardrobe"
            st.rerun()
    
    with col2:
        st.markdown("### Weather-Based Suggestions")
        if st.button("🌤️ Get Outfit Suggestions"):
            st.query_params["page"] = "Weather Outfits"
            st.rerun()

def main():
    # Apply custom styling - this should be after set_page_config but before other st commands
    st.markdown(set_custom_style(), unsafe_allow_html=True)
    initialize_session_state()
    
    st.markdown("""
        <h1 style='text-align: center; color: #2c3e50; padding: 2rem 0;'>
            👔 Your Digital Wardrobe
        </h1>
    """, unsafe_allow_html=True)

    if st.session_state.logged_in and st.session_state.username:
        if st.session_state.show_style_quiz:
            style_quizzes()
        elif st.session_state.get('show_tutorial', False):
            show_tutorial()
        else:
            page_function = show_navigation()
            page_function()
    else:
        show_welcome_message()
        handle_authentication()

if __name__ == "__main__":
    main()