from dataclasses import dataclass
import streamlit as st
import json
import os
from datetime import datetime
import uuid
from PIL import Image
from pydantic import BaseModel
import pandas as pd
import numpy as np
import time
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Add authentication functions
def hash_password(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def load_user_db():
    if not os.path.exists("users.csv"):
        df = pd.DataFrame(columns=["username", "password"])
        df.to_csv("users.csv", index=False)
    try:
        df = pd.read_csv("users.csv")
    except pd.errors.EmptyDataError:
        df = pd.DataFrame(columns=["username", "password"])
    return df

def verify_user(username, password):
    df = load_user_db()
    hashed_password = hash_password(password)
    if username in df["username"].values:
        stored_password = df[df["username"] == username]["password"].values[0]
        return stored_password == hashed_password
    return False

def login():
    st.title("Login to Style Community")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if verify_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid username or password")

# Models for social features
class Post(BaseModel):
    id: str
    user_id: str
    outfit_id: str 
    caption: str
    timestamp: str
    likes: list = []
    comments: list = []

class Comment(BaseModel):
    id: str
    user_id: str
    post_id: str
    text: str
    timestamp: str

# Social feature functions
def save_post(username, outfit_id, caption):
    """Save a new post"""
    post_file = "posts.json"
    try:
        # Load existing posts
        if os.path.exists(post_file):
            with open(post_file, 'r') as f:
                posts = json.load(f)
        else:
            posts = []
            
        # Create new post
        new_post = {
            "id": str(uuid.uuid4()),
            "user_id": username,
            "outfit_id": outfit_id,
            "caption": caption,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "likes": [],
            "comments": []
        }
        
        posts.append(new_post)
        
        # Save updated posts
        with open(post_file, 'w') as f:
            json.dump(posts, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Error saving post: {str(e)}")
        return False

def load_posts(username=None):
    """Load all posts or posts for a specific user"""
    post_file = "posts.json"
    try:
        if os.path.exists(post_file):
            with open(post_file, 'r') as f:
                posts = json.load(f)
                if username:
                    posts = [p for p in posts if p['user_id'] == username]
                return posts
        return []
    except Exception as e:
        st.error(f"Error loading posts: {str(e)}")
        return []

def toggle_like(post_id, username):
    """Toggle like on a post"""
    post_file = "posts.json"
    try:
        with open(post_file, 'r') as f:
            posts = json.load(f)
            
        for post in posts:
            if post['id'] == post_id:
                if username in post['likes']:
                    post['likes'].remove(username)
                else:
                    post['likes'].append(username)
                break
                
        with open(post_file, 'w') as f:
            json.dump(posts, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Error toggling like: {str(e)}")
        return False

def add_comment(post_id, username, text):
    """Add a comment to a post"""
    post_file = "posts.json"
    try:
        with open(post_file, 'r') as f:
            posts = json.load(f)
            
        for post in posts:
            if post['id'] == post_id:
                new_comment = {
                    "id": str(uuid.uuid4()),
                    "user_id": username,
                    "text": text,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                post['comments'].append(new_comment)
                break
                
        with open(post_file, 'w') as f:
            json.dump(posts, f, indent=2)
            
        return True
    except Exception as e:
        st.error(f"Error adding comment: {str(e)}")
        return False

def follow_user(follower, following):
    """Follow another user"""
    follows_file = "follows.json"
    try:
        if os.path.exists(follows_file):
            with open(follows_file, 'r') as f:
                follows = json.load(f)
        else:
            follows = {"follows": []}
            
        new_follow = {
            "follower": follower,
            "following": following,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Check if already following
        if not any(f['follower'] == follower and f['following'] == following for f in follows['follows']):
            follows['follows'].append(new_follow)
            
            with open(follows_file, 'w') as f:
                json.dump(follows, f, indent=2)
                
        return True
    except Exception as e:
        st.error(f"Error following user: {str(e)}")
        return False

def get_followers(username):
    """Get list of followers for a user"""
    follows_file = "follows.json"
    try:
        if os.path.exists(follows_file):
            with open(follows_file, 'r') as f:
                follows = json.load(f)
                return [f['follower'] for f in follows['follows'] if f['following'] == username]
        return []
    except Exception as e:
        st.error(f"Error getting followers: {str(e)}")
        return []

def get_following(username):
    """Get list of users being followed"""
    follows_file = "follows.json"
    try:
        if os.path.exists(follows_file):
            with open(follows_file, 'r') as f:
                follows = json.load(f)
                return [f['following'] for f in follows['follows'] if f['follower'] == username]
        return []
    except Exception as e:
        st.error(f"Error getting following: {str(e)}")
        return []

def display_social_feed():
    st.title("👗 Style Community")
    
    if "username" not in st.session_state:
        st.warning("Please log in to view the style community.")
        return
        
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["Feed", "Share Outfit", "Discover", "Profile"])
    
    with tab1:
        st.subheader("Style Feed")
        # Get current user's following list
        following = get_following(st.session_state.username)
        
        # Load all posts
        all_posts = load_posts()
        
        # Filter posts from followed users and self
        feed_posts = [p for p in all_posts if p['user_id'] in following or p['user_id'] == st.session_state.username]
        feed_posts.sort(key=lambda x: x['timestamp'], reverse=True)
        
        if not feed_posts:
            st.info("Follow other users to see their outfits here!")
            
        # Display posts
        for post in feed_posts:
            with st.container():
                st.markdown(f"""
                    <div style='padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 1rem;'>
                        <p><strong>@{post['user_id']}</strong></p>
                    """, unsafe_allow_html=True)
                
                # Display outfit images
                outfit_file = f"{post['user_id']}_outfits.json"
                if os.path.exists(outfit_file):
                    with open(outfit_file, 'r') as f:
                        outfits = json.load(f)
                        outfit = next((o for o in outfits if o['id'] == post['outfit_id']), None)
                        if outfit:
                            cols = st.columns(len(outfit['items']))
                            for idx, item in enumerate(outfit['items']):
                                with cols[idx]:
                                    if os.path.exists(item['image_path']):
                                        image = Image.open(item['image_path'])
                                        st.image(image, caption=item['name'], width=120)
                
                # Display caption
                st.markdown(f"<p>{post['caption']}</p>", unsafe_allow_html=True)
                
                # Like button and count
                col1, col2 = st.columns([1, 4])
                with col1:
                    if st.button(
                        "❤️" if st.session_state.username in post['likes'] else "🤍",
                        key=f"like_{post['id']}"
                    ):
                        toggle_like(post['id'], st.session_state.username)
                        st.rerun()
                with col2:
                    st.write(f"{len(post['likes'])} likes")
                
                # Comments
                with st.expander(f"View {len(post['comments'])} comments"):
                    for comment in post['comments']:
                        st.markdown(f"""
                            <p><strong>@{comment['user_id']}</strong> {comment['text']}</p>
                            """, unsafe_allow_html=True)
                    
                    # Add comment
                    new_comment = st.text_input("Add a comment", key=f"comment_{post['id']}")
                    if st.button("Post", key=f"post_comment_{post['id']}"):
                        if new_comment.strip():
                            add_comment(post['id'], st.session_state.username, new_comment)
                            st.rerun()
                
                st.markdown("<hr>", unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Share an Outfit")
        
        # Load user's outfits
        outfit_file = f"{st.session_state.username}_outfits.json"
        if os.path.exists(outfit_file):
            with open(outfit_file, 'r') as f:
                outfits = json.load(f)
                
            # Create outfit selection
            outfit_names = [outfit['name'] for outfit in outfits]
            selected_outfit = st.selectbox("Choose an outfit to share", outfit_names)
            
            if selected_outfit:
                outfit = next((o for o in outfits if o['name'] == selected_outfit), None)
                if outfit:
                    # Preview outfit
                    st.write("Preview:")
                    cols = st.columns(len(outfit['items']))
                    for idx, item in enumerate(outfit['items']):
                        with cols[idx]:
                            if os.path.exists(item['image_path']):
                                image = Image.open(item['image_path'])
                                st.image(image, caption=item['name'], width=120)
                    
                    # Add caption
                    caption = st.text_area("Write a caption...")
                    
                    if st.button("Share Outfit"):
                        if save_post(st.session_state.username, outfit['id'], caption):
                            st.success("Outfit shared successfully!")
                            st.rerun()
        else:
            st.info("Create some outfits first!")
    
    with tab3:
        st.subheader("Discover Users")
        
        # Load all users
        user_db = pd.read_csv("users.csv")
        following = get_following(st.session_state.username)
        
        # Filter out current user and already followed users
        discover_users = user_db[~user_db['username'].isin([st.session_state.username] + following)]
        
        for _, user in discover_users.iterrows():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"@{user['username']}")
                followers = get_followers(user['username'])
                st.write(f"{len(followers)} followers")
            with col2:
                if st.button("Follow", key=f"follow_{user['username']}"):
                    if follow_user(st.session_state.username, user['username']):
                        st.success(f"Now following @{user['username']}")
                        st.rerun()
    
    with tab4:
        st.subheader("My Profile")
        
        followers = get_followers(st.session_state.username)
        following = get_following(st.session_state.username)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Posts", len(load_posts(st.session_state.username)))
        with col2:
            st.metric("Followers", len(followers))
        with col3:
            st.metric("Following", len(following))
        
        # Display user's posts
        st.write("My Posts")
        user_posts = load_posts(st.session_state.username)
        for post in user_posts:
            # Display post (similar to feed display)
            with st.container():
                st.markdown(f"""
                    <div style='padding: 1rem; border: 1px solid #ddd; border-radius: 8px; margin-bottom: 1rem;'>
                        <p><strong>@{post['user_id']}</strong></p>
                    """, unsafe_allow_html=True)
                
                # Display outfit images
                outfit_file = f"{post['user_id']}_outfits.json"
                if os.path.exists(outfit_file):
                    with open(outfit_file, 'r') as f:
                        outfits = json.load(f)
                        outfit = next((o for o in outfits if o['id'] == post['outfit_id']), None)
                        if outfit:
                            cols = st.columns(len(outfit['items']))
                            for idx, item in enumerate(outfit['items']):
                                with cols[idx]:
                                    if os.path.exists(item['image_path']):
                                        image = Image.open(item['image_path'])
                                        st.image(image, caption=item['name'], width=120)
                
                st.markdown(f"<p>{post['caption']}</p>", unsafe_allow_html=True)
                st.write(f"{len(post['likes'])} likes • {len(post['comments'])} comments")

def main():
    # Add custom CSS
    st.markdown("""
        <style>
        .stApp {
            max-width: 1200px;
            margin: 0 auto;
        }
        .post-container {
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    # Check login state
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login()
    else:
        # Add logout button to sidebar
        if st.sidebar.button("Logout"):
            st.session_state.clear()
            st.rerun()

        # Link back to main app
        st.sidebar.markdown("[Go to Main Wardrobe App](http://localhost:8501)")
            
        display_social_feed()

if __name__ == "__main__":
    main() 