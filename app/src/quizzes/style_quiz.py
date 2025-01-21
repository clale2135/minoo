import streamlit as st
from openai import OpenAI
import json
from datetime import datetime
import os

def analyze_color_season(responses):
    """Analyze quiz responses to determine color season"""
    prompt = f"""Based on these characteristics:
    Skin undertone: {responses['skin_undertone']}
    Natural hair color: {responses['hair_color']}
    Eye color: {responses['eye_color']}
    Best jewelry: {responses['jewelry']}
    Sun reaction: {responses['sun_reaction']}
    
    Determine the person's color season (Spring, Summer, Autumn, or Winter) and specify if it's warm or cool.
    Return ONLY the season name in this format: "Warm Spring" or "Cool Winter" etc."""
    
    client = OpenAI()  # Make sure you have OPENAI_API_KEY in your environment
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a color analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_color_results(season):
    """Display color analysis results"""
    st.success(f"Your Color Season: {season}")
    
    # Color recommendations based on season
    colors = get_season_colors(season)
    
    st.markdown("### Your Best Colors")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Recommended Colors")
        for color in colors['recommended']:
            st.markdown(f"- {color}")
    
    with col2:
        st.markdown("#### Colors to Avoid")
        for color in colors['avoid']:
            st.markdown(f"- {color}")
    
    st.markdown("### Styling Tips")
    st.markdown(get_season_tips(season))

def analyze_face_shape(responses):
    """Analyze quiz responses to determine face shape"""
    prompt = f"""Based on these facial characteristics:
    Face length: {responses['face_length']}
    Jaw shape: {responses['jaw_shape']}
    Cheekbones: {responses['cheekbones']}
    
    Determine the person's face shape (Oval, Round, Square, Heart, Diamond, or Rectangle).
    Return ONLY the face shape name."""
    
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a facial analysis expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def show_face_shape_results(face_shape):
    """Display face shape analysis results"""
    st.success(f"Your Face Shape: {face_shape}")
    
    # Get recommendations based on face shape
    recommendations = get_face_shape_recommendations(face_shape)
    
    st.markdown("### Style Recommendations")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Recommended")
        for rec in recommendations['recommended']:
            st.markdown(f"- {rec}")
    
    with col2:
        st.markdown("#### Avoid")
        for avoid in recommendations['avoid']:
            st.markdown(f"- {avoid}")

def get_face_shape_recommendations(face_shape):
    """Get style recommendations based on face shape"""
    recommendations = {
        'Oval': {
            'recommended': [
                "Most hairstyles and accessories",
                "Balanced necklines",
                "Medium-sized jewelry"
            ],
            'avoid': [
                "Very heavy bangs",
                "Oversized accessories",
                "Extreme styles"
            ]
        },
        'Round': {
            'recommended': [
                "Angular frames",
                "V-neck and deep necklines",
                "Long necklaces"
            ],
            'avoid': [
                "Round frames",
                "Choker necklaces",
                "Round necklines"
            ]
        }
        # Add more face shapes and recommendations as needed
    }
    
    return recommendations.get(face_shape, {
        'recommended': ["Balanced styles", "Classic cuts", "Moderate accessories"],
        'avoid': ["Extreme styles", "Overwhelming accessories"]
    })

def get_season_colors(season):
    """Get color recommendations based on season"""
    colors = {
        'Warm Spring': {
            'recommended': ["Warm yellow", "Coral", "Peach", "Golden brown"],
            'avoid': ["Black", "Gray", "Cool blues"]
        },
        'Cool Winter': {
            'recommended': ["Pure white", "Navy", "Cool red", "Royal blue"],
            'avoid': ["Orange", "Warm browns", "Muted colors"]
        }
        # Add more seasons and color recommendations as needed
    }
    
    return colors.get(season, {
        'recommended': ["Neutral colors", "Classic shades"],
        'avoid': ["Extreme contrasts", "Overwhelming colors"]
    })

def get_season_tips(season):
    """Get styling tips based on color season"""
    tips = {
        'Warm Spring': """
        - Focus on warm, clear colors
        - Choose gold jewelry
        - Avoid dark, heavy colors
        """,
        'Cool Winter': """
        - Wear high-contrast combinations
        - Choose silver jewelry
        - Avoid muted or warm colors
        """
        # Add more seasons and tips as needed
    }
    
    return tips.get(season, """
        - Stick to classic color combinations
        - Choose versatile jewelry metals
        - Focus on what makes you feel confident
    """)

def body_type_quiz():
    """Quiz to determine user's body type"""
    st.markdown("### 📏 Body Type Analysis")
    # ... rest of the function implementation ...

def style_personality_quiz():
    """Quiz to determine user's style personality"""
    st.markdown("### 👗 Style Personality Quiz")
    # ... rest of the function implementation ...

def wardrobe_essentials_quiz():
    """Quiz to determine essential pieces for user's lifestyle"""
    st.markdown("### 👔 Wardrobe Essentials Quiz")
    # ... rest of the function implementation ...

def color_analysis_quiz():
    """Quiz to determine user's color season"""
    st.markdown("### 🎨 Color Analysis Quiz")
    st.markdown("""
        Let's find your color season! Answer these questions about your natural coloring.
        This will help you choose colors that enhance your natural beauty.
    """)
    
    questions = {
        'skin_undertone': {
            'question': "What are the undertones of your skin?",
            'options': [
                "Warm (golden, peachy, or yellow)",
                "Cool (pink, red, or blue)",
                "Neutral (mix of warm and cool)",
                "Not sure"
            ],
            'help': "Look at the veins on your wrist - green veins suggest warm, blue/purple suggest cool"
        },
        'hair_color': {
            'question': "What's your natural hair color?",
            'options': [
                "Golden blonde",
                "Ash blonde",
                "Warm brown",
                "Cool brown",
                "Black",
                "Red/Auburn",
                "Gray/Silver"
            ]
        },
        'eye_color': {
            'question': "What's your eye color?",
            'options': [
                "Warm brown",
                "Cool brown",
                "Hazel",
                "Green",
                "Blue",
                "Gray"
            ]
        },
        'jewelry': {
            'question': "Which metal jewelry looks best on you?",
            'options': [
                "Gold",
                "Silver",
                "Both look equally good",
                "Rose gold"
            ]
        },
        'sun_reaction': {
            'question': "How does your skin react to sun exposure?",
            'options': [
                "Tans easily, rarely burns",
                "Burns easily, rarely tans",
                "Burns first, then tans",
                "Never burns or tans much"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            help=data.get('help', None),
            key=f"color_{key}"
        )
        st.markdown("---")
    
    if st.button("Analyze My Colors", type="primary"):
        season = analyze_color_season(responses)
        show_color_results(season)

def face_shape_quiz():
    """Quiz to determine user's face shape"""
    st.markdown("### 👤 Face Shape Analysis")
    st.markdown("""
        Understanding your face shape helps you choose the most flattering:
        - Hairstyles
        - Glasses frames
        - Necklines
        - Accessories
    """)
    
    questions = {
        'face_length': {
            'question': "How would you describe your face length?",
            'options': [
                "Longer than it is wide",
                "About equal in length and width",
                "Wider than it is long"
            ]
        },
        'jaw_shape': {
            'question': "Which best describes your jaw?",
            'options': [
                "Angular and sharp",
                "Rounded",
                "Square and prominent",
                "Narrow and pointed"
            ]
        },
        'cheekbones': {
            'question': "How would you describe your cheekbones?",
            'options': [
                "High and prominent",
                "Round and full",
                "Not very prominent",
                "Wide and angular"
            ]
        }
    }
    
    responses = {}
    for key, data in questions.items():
        responses[key] = st.radio(
            data['question'],
            data['options'],
            key=f"face_{key}"
        )
        st.markdown("---")
    
    if st.button("Analyze My Face Shape", type="primary"):
        face_shape = analyze_face_shape(responses)
        show_face_shape_results(face_shape)

def style_quizzes():
    """Interactive quizzes for personal style education"""
    st.title("📚 Style Education & Quizzes")
    
    # Quiz Selection
    quiz_type = st.selectbox(
        "Choose a Quiz Topic",
        ["Color Analysis", "Face Shape", "Body Type", "Style Personality", "Wardrobe Essentials"]
    )
    
    if quiz_type == "Color Analysis":
        color_analysis_quiz()
    elif quiz_type == "Face Shape":
        face_shape_quiz()
    elif quiz_type == "Body Type":
        body_type_quiz()
    elif quiz_type == "Style Personality":
        style_personality_quiz()
    elif quiz_type == "Wardrobe Essentials":
        wardrobe_essentials_quiz()

def save_color_analysis(username, analysis):
    """Save user's color analysis to their profile"""
    try:
        profile_file = f"{username}_profile.json"
        
        # Load existing profile or create new one
        if os.path.exists(profile_file):
            with open(profile_file, 'r') as f:
                profile_data = json.load(f)
        else:
            profile_data = {}
        
        # Update with color analysis
        profile_data['color_analysis'] = {
            'season': analysis['season'],
            'best_colors': analysis['best_colors'],
            'avoid_colors': analysis['avoid_colors'],
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Save updated profile
        with open(profile_file, 'w') as f:
            json.dump(profile_data, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving color analysis: {str(e)}")

def show_tutorial():
    """Display the getting started tutorial"""
    st.title("🎯 Getting Started with Your Digital Wardrobe")
    
    st.markdown("""
        Welcome to your personalized digital wardrobe! Let's get you started:
        
        1. **Add Your Clothes** 📸
           - Upload photos of your clothing items
           - Our AI will help categorize them
           - Add details like color, season, and occasion
        
        2. **Explore Features** 🔍
           - Get weather-based outfit suggestions
           - Create and save outfit combinations
           - Schedule outfits for upcoming events
        
        3. **Take Style Quizzes** 🎨
           - Discover your color season
           - Learn your body type
           - Find your style personality
    """)
    
    if st.button("Got it! Let's Start"):
        st.session_state.show_tutorial = False
        st.rerun() 