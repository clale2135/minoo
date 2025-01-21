<<<<<<< HEAD
"""Color analysis module for determining user's color season"""

def analyze_colors_with_imagga(image_bytes):
    """Analyze colors in an image using Imagga API"""
    # Placeholder for actual API implementation
    return []

def determine_color_season(colors_data):
    """Determine a user's color season based on their coloring"""
    # Placeholder implementation
    return "Spring"

def get_season_colors(season):
    """Get the color palette for a given season"""
    season_colors = {
        "Spring": ["Warm Yellow", "Coral", "Peach", "Light Green", "Aqua"],
        "Summer": ["Soft Pink", "Lavender", "Light Blue", "Mint", "Gray"],
        "Autumn": ["Rust", "Olive", "Warm Brown", "Terracotta", "Gold"],
        "Winter": ["Pure White", "Black", "Royal Blue", "Deep Purple", "True Red"]
    }
    return season_colors.get(season, []) 
=======
import streamlit as st
import requests
import os
import json
from PIL import Image
import io
import openai

def analyze_colors_with_imagga(image_bytes):
    """Analyze image colors using Imagga API to extract skin, hair, and eye colors"""
    api_key = os.getenv("IMAGGA_API_KEY")
    api_secret = os.getenv("IMAGGA_API_SECRET")
    
    if not api_key or not api_secret:
        st.error("Imagga API credentials not found. Please check your .env file.")
        return None
    
    try:
        api_url = "https://api.imagga.com/v2/colors"
        files = {'image': image_bytes}
        
        response = requests.post(
            api_url,
            auth=(api_key, api_secret),
            files=files
        )
        
        if response.status_code == 200:
            data = response.json()
            colors = data['result']['colors']
            
            # Extract dominant colors for skin, hair, and eyes
            # We'll use foreground colors for face features and background for skin
            return {
                'skin_tone': colors['background_colors'][0]['html_code'],
                'hair_color': colors['foreground_colors'][0]['html_code'],
                'eye_color': colors['foreground_colors'][1]['html_code'] if len(colors['foreground_colors']) > 1 else colors['foreground_colors'][0]['html_code']
            }
        else:
            st.error(f"Error from Imagga API: {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Error accessing Imagga API: {str(e)}")
        return None

def determine_color_season(colors_data):
    """Use GPT-4 to determine color season based on extracted colors"""
    if not colors_data:
        return None
    
    prompt = f"""Based on this person's coloring:
    
    Skin tone (hex code): {colors_data['skin_tone']}
    Hair color (hex code): {colors_data['hair_color']}
    Eye color (hex code): {colors_data['eye_color']}
    
    Please determine:
    1. Their color season (Spring, Summer, Autumn, or Winter)
    2. Whether they have warm or cool undertones
    3. A list of 5-7 specific colors that would be most flattering for them to wear
    4. A brief explanation of why this season suits them based on their coloring
    
    Consider these guidelines:
    - Spring: Warm and bright colors
    - Summer: Cool and soft colors
    - Autumn: Warm and muted colors
    - Winter: Cool and bright colors
    
    Return your response in this exact JSON format:
    {{
        "season": "Season name with temperature (e.g., 'Warm Spring', 'Cool Summer')",
        "undertone": "Warm or Cool",
        "flattering_colors": ["color1", "color2", "etc"],
        "explanation": "Brief explanation of the analysis"
    }}"""
    
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a professional color analyst expert."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error in color analysis: {str(e)}")
        return None

def get_season_colors(season):
    """Get recommended and avoid colors for a season"""
    color_recommendations = {
        "Warm Spring": {
            "recommended": [
                "Warm Yellow",
                "Coral",
                "Peach",
                "Warm Green",
                "Golden Brown",
                "Bright Orange",
                "Spring Green"
            ],
            "avoid": [
                "Deep Purple",
                "Cool Gray",
                "Black",
                "Navy Blue",
                "Cool Pink"
            ]
        },
        "Cool Summer": {
            "recommended": [
                "Soft Pink",
                "Powder Blue",
                "Lavender",
                "Sage Green",
                "Cool Gray",
                "Periwinkle",
                "Mauve"
            ],
            "avoid": [
                "Orange",
                "Bright Yellow",
                "Tomato Red",
                "Warm Brown",
                "Gold"
            ]
        },
        "Warm Autumn": {
            "recommended": [
                "Rust",
                "Olive Green",
                "Warm Brown",
                "Terracotta",
                "Bronze",
                "Forest Green",
                "Burnt Orange"
            ],
            "avoid": [
                "Cool Pink",
                "Ice Blue",
                "Pure White",
                "Cool Purple",
                "Silver"
            ]
        },
        "Cool Winter": {
            "recommended": [
                "Pure White",
                "Navy Blue",
                "Cool Red",
                "Royal Purple",
                "Ice Pink",
                "Emerald",
                "True Black"
            ],
            "avoid": [
                "Orange",
                "Warm Brown",
                "Olive Green",
                "Coral",
                "Gold"
            ]
        }
    }
    
    # Handle variations in season names
    for key in list(color_recommendations.keys()):
        if season.lower() in key.lower():
            return color_recommendations[key]
    
    # Default recommendations if season doesn't match exactly
    return {
        "recommended": ["Navy", "Gray", "White", "Black", "Blue"],
        "avoid": ["Neon Colors", "Very Bright Colors", "Clashing Colors"]
    }

def get_color_info(color):
    """Get color information from a hex code or color name"""
    try:
        if not color.startswith('#'):
            url = f"https://www.thecolorapi.com/id?name={color}&format=json"
            response = requests.get(url)
            data = response.json()
            hex_code = data['hex']['value']
            name = color
        else:
            hex_code = color
            url = f"https://www.thecolorapi.com/id?hex={color.lstrip('#')}&format=json"
            response = requests.get(url)
            data = response.json()
            name = data['name']['value']
        
        return {
            'hex': hex_code,
            'name': name,
            'rgb': data['rgb']['value'],
            'hsl': data['hsl']['value']
        }
    except Exception as e:
        st.error(f"Error getting color information: {str(e)}")
        return {
            'hex': color,
            'name': color,
            'rgb': color,
            'hsl': color
        }

def get_image_colors(image_bytes):
    """Extract colors from image using Imagga API"""
    api_key = os.getenv("IMAGGA_API_KEY")
    api_secret = os.getenv("IMAGGA_API_SECRET")
    
    url = "https://api.imagga.com/v2/colors"
    
    headers = {
        'accept': 'application/json',
        'authorization': f'Basic {api_key}:{api_secret}'
    }
    
    files = {'image': image_bytes}
    
    try:
        response = requests.post(url, headers=headers, files=files)
        data = response.json()
        
        if response.status_code == 200:
            colors = data['result']['colors']
            
            return {
                'background': colors.get('background_colors', []),
                'foreground': colors.get('foreground_colors', []),
                'image': colors.get('image_colors', [])
            }
        else:
            st.error(f"API Error: {data.get('status', {}).get('text', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"Error calling Imagga API: {str(e)}")
        return None

def show_color_swatch(hex_color, name):
    """Display a color swatch with name and hex code"""
    # Convert color names to hex if needed
    if not hex_color.startswith('#'):
        try:
            response = requests.get(f"https://www.thecolorapi.com/id?name={hex_color}")
            hex_color = response.json()['hex']['value']
        except:
            hex_color = "#808080"  # Default to gray if conversion fails
    
    st.markdown(f"""
        <div class="color-swatch-container" style="
            display: inline-flex;
            align-items: center;
            margin: 10px;
            padding: 10px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border: 1px solid rgba(212,176,140,0.2);
        ">
            <div class="color-swatch" style='
                background-color: {hex_color}; 
                width: 80px; 
                height: 80px; 
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border: 1px solid rgba(0,0,0,0.05);
            '></div>
            <div style='
                margin-left: 15px;
                font-family: "Playfair Display", serif;
            '>
                <div style='
                    color: #2C1810;
                    font-size: 1.1rem;
                    margin-bottom: 4px;
                '>{name}</div>
                <div style='
                    color: #8B7355;
                    font-size: 0.9rem;
                    font-family: monospace;
                '>{hex_color}</div>
            </div>
        </div>
    """, unsafe_allow_html=True) 
>>>>>>> 82784ae66500dcd327bb26ca80802df0894371fb
