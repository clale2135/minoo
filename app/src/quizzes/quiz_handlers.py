import streamlit as st
import pandas as pd
import json
from openai import OpenAI
import os
from PIL import Image
import io
from src.styles.color_analysis import (
    analyze_colors_with_imagga,
    determine_color_season,
    get_season_colors,
    show_color_swatch
)

def style_quizzes():
    """Main entry point for all style quizzes"""
    st.title("Style Quizzes")
    quiz_options = [
        "Color Analysis",
        "Face Shape Analysis",
        "Body Type Analysis",
        "Style Personality",
        "Wardrobe Essentials"
    ]
    selected_quiz = st.selectbox("Choose a quiz:", quiz_options)
    
    if selected_quiz == "Color Analysis":
        color_analysis_quiz()
    elif selected_quiz == "Face Shape Analysis":
        face_shape_quiz()
    elif selected_quiz == "Body Type Analysis":
        body_type_quiz()
    elif selected_quiz == "Style Personality":
        style_personality_quiz()
    elif selected_quiz == "Wardrobe Essentials":
        wardrobe_essentials_quiz()

def color_analysis_quiz():
    """Quiz to determine user's color season using hex codes"""
    st.title("Color Analysis Quiz")
    st.write("Enter the hex codes for your natural hair color, eye color, and skin color to determine your color season.")
    
    # Color input section
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Hair Color")
        hair_color = st.color_picker("Select your natural hair color", "#000000")
        st.markdown(f"Selected hair color: `{hair_color}`")
    
    with col2:
        st.subheader("Eye Color")
        eye_color = st.color_picker("Select your eye color", "#000000")
        st.markdown(f"Selected eye color: `{eye_color}`")
    
    with col3:
        st.subheader("Skin Color")
        skin_color = st.color_picker("Select your skin color", "#000000")
        st.markdown(f"Selected skin color: `{skin_color}`")
    
    # Additional questions
    st.subheader("Additional Information")
    jewelry_preference = st.radio(
        "Which metal jewelry looks best on you?",
        ["Gold", "Silver", "Both look equally good", "Rose gold"]
    )
    
    sun_reaction = st.radio(
        "How does your skin react to sun exposure?",
        ["Tans easily, rarely burns", "Burns easily, rarely tans", "Burns first, then tans", "Never burns or tans much"]
    )
    
    if st.button("Analyze My Colors", type="primary"):
        with st.spinner("Analyzing your colors..."):
            # Prepare data for analysis
            color_data = {
                "hair_color": hair_color,
                "eye_color": eye_color,
                "skin_color": skin_color,
                "jewelry_preference": jewelry_preference,
                "sun_reaction": sun_reaction
            }
            
            # Analyze colors using GPT
            analysis = analyze_colors_with_gpt(color_data)
            
            if analysis:
                st.success("Analysis complete!")
                
                # Display results
                st.markdown('<h2 style="color: #000000;">Your Color Season</h2>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #000000; font-size: 1.2em;">You are a {analysis["season"]} with {analysis["undertone"]} undertones.</p>', unsafe_allow_html=True)
                
                st.markdown('<h3 style="color: #000000;">Analysis Explanation</h3>', unsafe_allow_html=True)
                st.markdown(f'<p style="color: #000000;">{analysis["explanation"]}</p>', unsafe_allow_html=True)
                
                st.markdown('<h3 style="color: #000000;">Your Most Flattering Colors</h3>', unsafe_allow_html=True)
                # Create columns for flattering colors
                num_colors = len(analysis['flattering_colors'])
                color_cols = st.columns(num_colors)
                
                # Display colors in horizontal row
                for idx, color in enumerate(analysis['flattering_colors']):
                    with color_cols[idx]:
                        show_color_swatch(color, color)
                
                # Get and display season-specific recommendations
                season_colors = get_season_colors(analysis['season'])
                
                st.markdown('<h3 style="color: #000000;">Recommended Colors</h3>', unsafe_allow_html=True)
                # Create columns for recommended colors
                num_recommended = len(season_colors['recommended'])
                recommended_cols = st.columns(num_recommended)
                
                # Display recommended colors in horizontal row
                for idx, color in enumerate(season_colors['recommended']):
                    with recommended_cols[idx]:
                        show_color_swatch(color, color)
                
                st.markdown('<h3 style="color: #000000;">Colors to Avoid</h3>', unsafe_allow_html=True)
                # Create columns for colors to avoid
                num_avoid = len(season_colors['avoid'])
                avoid_cols = st.columns(num_avoid)
                
                # Display colors to avoid in horizontal row
                for idx, color in enumerate(season_colors['avoid']):
                    with avoid_cols[idx]:
                        show_color_swatch(color, color)
                
                # Save the analysis to user's profile
                if st.button("Save Analysis to Profile"):
                    save_color_analysis(st.session_state.username, analysis)
                    st.success("Color analysis saved to your profile!")
            else:
                st.error("Could not complete the color analysis. Please try again.")

def analyze_colors_with_gpt(color_data):
    """Analyze colors using GPT to determine color season"""
    prompt = f"""Based on these color characteristics:
    Hair color (hex): {color_data['hair_color']}
    Eye color (hex): {color_data['eye_color']}
    Skin color (hex): {color_data['skin_color']}
    Jewelry preference: {color_data['jewelry_preference']}
    Sun reaction: {color_data['sun_reaction']}
    
    Determine the person's color season (Spring, Summer, Autumn, or Winter) and specify if it's warm or cool.
    Also provide:
    1. A detailed explanation of why this season was chosen
    2. A list of flattering colors for this season
    3. The undertone (warm, cool, or neutral)
    
    Return the response in JSON format with these keys:
    - season: the determined color season
    - undertone: warm, cool, or neutral
    - explanation: detailed explanation
    - flattering_colors: list of recommended colors
    
    Format your response as a valid JSON object."""
    
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a color analysis expert. Analyze the provided colors and characteristics to determine the person's color season. Always respond with a valid JSON object."},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Extract the JSON from the response
        response_text = response.choices[0].message.content
        # Find the JSON object in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        json_str = response_text[start_idx:end_idx]
        
        return json.loads(json_str)
    except Exception as e:
        st.error(f"Error analyzing colors: {str(e)}")
        return None

def face_shape_quiz():
    """Quiz to determine user's face shape"""
    st.title("Face Shape Analysis")
    # Quiz implementation...

def body_type_quiz():
    """Quiz to determine user's body type"""
    st.title("Body Type Quiz")
    # Quiz implementation...

def style_personality_quiz():
    """Quiz to determine user's style personality"""
    st.title("Style Personality Quiz")
    # Quiz implementation...

def wardrobe_essentials_quiz():
    """Quiz to determine essential pieces for user's lifestyle"""
    st.title("Wardrobe Essentials Quiz")
    # Quiz implementation...

def analyze_style_personality(responses):
    """Analyze user's style personality based on quiz responses"""
    # Analysis implementation...
    pass

def show_style_personality_results(personality_analysis):
    """Display style personality quiz results"""
    # Results display implementation...
    pass

def get_style_recommendations(primary, secondary):
    """Get style recommendations based on primary and secondary style types"""
    # Style recommendations implementation...
    pass

def analyze_wardrobe_essentials(responses):
    # Analysis implementation...
    pass

def show_wardrobe_essentials_results(essentials):
    # Results display implementation...
    pass

def analyze_face_shape(responses):
    # Analysis implementation...
    pass

def show_face_shape_results(face_shape):
    """Display face shape analysis results"""
    # Results display implementation...
    pass

def get_face_shape_tips(face_shape):
    # Tips implementation...
    pass

def analyze_body_type(responses):
    # Analysis implementation...
    pass

def show_body_type_results(body_type):
    """Display body type analysis results"""
    # Results display implementation...
    pass

def save_color_analysis(username, analysis):
    """Save color analysis results to user's profile"""
    try:
        # Get database connection
        conn = get_db()
        c = conn.cursor()
        
        # Create color_analysis table if it doesn't exist
        c.execute('''
            CREATE TABLE IF NOT EXISTS color_analysis (
                username TEXT PRIMARY KEY,
                season TEXT,
                undertone TEXT,
                explanation TEXT,
                flattering_colors TEXT,
                analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Save the analysis
        c.execute('''
            INSERT OR REPLACE INTO color_analysis 
            (username, season, undertone, explanation, flattering_colors)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            username,
            analysis['season'],
            analysis['undertone'],
            analysis['explanation'],
            json.dumps(analysis['flattering_colors'])
        ))
        
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error saving color analysis: {str(e)}")

def show_example_outfits(color_season):
    # Example outfits display implementation...
    pass 