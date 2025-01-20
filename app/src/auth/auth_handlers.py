import streamlit as st
import hashlib
import pandas as pd
import os

USER_DB_PATH = "user_db.csv"

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
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.show_style_quiz = True
            st.rerun() 