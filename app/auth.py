import streamlit as st
import functools

def require_auth(func):
    """Decorator to require authentication for accessing features"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not st.session_state.get("logged_in", False):
            st.warning("Please log in to access this feature.")
            tab1, tab2 = st.tabs(["Login", "Create Account"])
            with tab1:
                from app import login
                login()
            with tab2:
                from app import create_account
                create_account()
            return
        return func(*args, **kwargs)
    return wrapper 