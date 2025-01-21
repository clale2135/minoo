import streamlit as st
import pandas as pd
import json
from datetime import datetime
import os
from PIL import Image
import openai

def load_saved_outfits():
    """Load user's saved outfits"""
    outfits_file = f"{st.session_state.username}_outfits.json"
    if os.path.exists(outfits_file):
        with open(outfits_file, 'r') as f:
            return json.load(f)
    return []

def save_outfit(outfit_items, outfit_name, occasion):
    """Save a new outfit"""
    outfits = load_saved_outfits()
    
    new_outfit = {
        'name': outfit_name,
        'items': outfit_items,
        'occasion': occasion,
        'date_created': datetime.now().strftime("%Y-%m-%d")
    }
    
    outfits.append(new_outfit)
    
    outfits_file = f"{st.session_state.username}_outfits.json"
    with open(outfits_file, 'w') as f:
        json.dump(outfits, f, indent=4)

def display_saved_outfits():
    """Display user's saved outfits"""
    st.title("👔 Saved Outfits")
    
    outfits = load_saved_outfits()
    if not outfits:
        st.info("No saved outfits yet!")
        return
    
    # Filter options
    occasion_filter = st.multiselect(
        "Filter by occasion",
        options=list(set(outfit['occasion'] for outfit in outfits))
    )
    
    filtered_outfits = outfits
    if occasion_filter:
        filtered_outfits = [
            outfit for outfit in outfits 
            if outfit['occasion'] in occasion_filter
        ]
    
    # Display outfits
    for outfit in filtered_outfits:
        with st.expander(f"{outfit['name']} ({outfit['occasion']})"):
            st.write(f"Created on: {outfit['date_created']}")
            st.write("Items:")
            for item in outfit['items']:
                st.write(f"- {item}")
            
            if st.button("Delete Outfit", key=f"delete_{outfit['name']}"):
                outfits.remove(outfit)
                outfits_file = f"{st.session_state.username}_outfits.json"
                with open(outfits_file, 'w') as f:
                    json.dump(outfits, f, indent=4)
                st.success("Outfit deleted!")
                st.rerun()

def schedule_outfits():
    """Schedule outfits for different days"""
    st.title("📅 Outfit Calendar")
    
    schedule_file = f"{st.session_state.username}_outfit_schedule.json"
    outfits = load_saved_outfits()
    
    if not outfits:
        st.warning("You need to save some outfits first!")
        return
    
    # Load existing schedule
    schedule = load_outfit_schedule(schedule_file)
    
    # Calendar view
    month = st.selectbox("Select month:", range(1, 13))
    
    # Create calendar
    calendar = create_month_calendar(month, schedule, outfits)
    st.write(calendar)
    
    # Add new schedule
    st.subheader("Schedule an Outfit")
    date = st.date_input("Select date")
    outfit = st.selectbox("Select outfit", [outfit['name'] for outfit in outfits])
    
    if st.button("Schedule Outfit"):
        schedule[date.strftime("%Y-%m-%d")] = outfit
        save_outfit_schedule(schedule_file, schedule)
        st.success("Outfit scheduled!")
        st.rerun()

def load_outfit_schedule(schedule_file):
    """Load the outfit schedule"""
    if os.path.exists(schedule_file):
        with open(schedule_file, 'r') as f:
            return json.load(f)
    return {}

def save_outfit_schedule(schedule_file, schedule):
    """Save the outfit schedule"""
    with open(schedule_file, 'w') as f:
        json.dump(schedule, f, indent=4)

def create_month_calendar(month, schedule, outfits):
    """Create a calendar view of scheduled outfits"""
    # Calendar implementation...
    pass 

def generate_outfit_with_gpt(user_clothing_df, user_request=None, occasion=None, season=None, style_preference=None):
    """Generate outfit suggestions using GPT-4"""
    try:
        # Convert DataFrame to a formatted string of available items
        available_items = user_clothing_df.to_dict('records')
        items_str = "\n".join([
            f"- {item['name']} ({item['type_of_clothing']}, {item['color']}, for {item['season']} seasons)"
            for item in available_items
        ])

        # Create the prompt
        prompt = f"""As a professional fashion stylist, create an outfit from these available clothes:

Available Items:
{items_str}

User's Request: {user_request if user_request else 'Create a stylish outfit'}

Additional Requirements:
{f'Occasion: {occasion}' if occasion else ''}
{f'Season: {season}' if season else ''}
{f'Style Preference: {style_preference}' if style_preference else ''}

Please create a cohesive outfit that matches the user's request and works well together. Consider color coordination, style matching, and appropriateness for the occasion and season.

Return your response in this exact JSON format:
{{
    "outfit_items": ["item1_name", "item2_name", ...],
    "styling_tips": "Brief styling tips and suggestions",
    "color_coordination": "Explanation of color harmony",
    "occasion_appropriateness": "Why this outfit works for the request"
}}"""

        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert fashion stylist."},
                {"role": "user", "content": prompt}
            ]
        )

        # Parse the response
        outfit_suggestion = json.loads(response.choices[0].message.content)
        return outfit_suggestion

    except Exception as e:
        st.error(f"Error generating outfit: {str(e)}")
        return None

def display_outfit_generator():
    """Display the outfit generator interface"""
    st.title("✨ AI Outfit Generator")
    
    try:
        # Load user's clothing data
        user_clothing = pd.read_csv(f"{st.session_state.username}_clothing.csv")
        
        if len(user_clothing) == 0:
            st.info("Add some clothes to your wardrobe first!")
            return

        # Outfit generation options
        st.subheader("Generate Your Outfit")
        
        # Add text input for natural language request
        user_request = st.text_input(
            "What kind of outfit are you looking for?",
            placeholder="E.g., 'A casual outfit for a coffee date' or 'Something professional for a business meeting'"
        )
        
        # Make other options optional
        st.write("Optional additional preferences:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            occasion = st.selectbox(
                "Occasion",
                ["Any", "Casual", "Formal", "Business", "Party", "Date Night", "Outdoor", "Workout"],
                index=0
            )
        
        with col2:
            season = st.selectbox(
                "Season",
                ["Any", "Spring", "Summer", "Fall", "Winter"],
                index=0
            )
        
        with col3:
            style_preference = st.selectbox(
                "Style Preference",
                ["Any", "Classic", "Modern", "Bohemian", "Minimalist", "Streetwear", "Elegant", "Sporty"],
                index=0
            )
        
        if st.button("Generate Outfit"):
            with st.spinner("Creating your perfect outfit..."):
                # Only pass non-"Any" values to the generator
                outfit = generate_outfit_with_gpt(
                    user_clothing,
                    user_request=user_request,
                    occasion=None if occasion == "Any" else occasion,
                    season=None if season == "Any" else season,
                    style_preference=None if style_preference == "Any" else style_preference
                )
                
                if outfit:
                    # Display the generated outfit
                    st.success("Outfit generated successfully!")
                    
                    # Display selected items
                    st.subheader("Selected Items")
                    selected_items = user_clothing[user_clothing['name'].isin(outfit['outfit_items'])]
                    
                    # Create columns for each item
                    cols = st.columns(len(selected_items))
                    for idx, (_, item) in enumerate(selected_items.iterrows()):
                        with cols[idx]:
                            try:
                                if os.path.exists(item['image_path']):
                                    st.image(item['image_path'], caption=item['name'], width=150)
                                st.write(f"**{item['name']}**")
                                st.write(f"Type: {item['type_of_clothing']}")
                                st.write(f"Color: {item['color']}")
                            except Exception as e:
                                st.error(f"Error displaying item: {str(e)}")
                    
                    # Display styling advice
                    st.subheader("Styling Tips")
                    st.write(outfit['styling_tips'])
                    
                    st.subheader("Color Coordination")
                    st.write(outfit['color_coordination'])
                    
                    st.subheader("Perfect For Your Request")
                    st.write(outfit['occasion_appropriateness'])
                    
                    # Option to save the outfit
                    if st.button("Save This Outfit"):
                        # Use the user's request as part of the outfit name
                        request_summary = user_request[:30] + "..." if len(user_request) > 30 else user_request
                        save_generated_outfit(
                            outfit_items=outfit['outfit_items'],
                            styling_tips=outfit['styling_tips'],
                            occasion=request_summary,
                            season=season if season != "Any" else None,
                            style=style_preference if style_preference != "Any" else None
                        )
                        st.success("Outfit saved to your collection!")

    except FileNotFoundError:
        st.info("Please add some clothes to your wardrobe first!")
    except Exception as e:
        st.error(f"Error in outfit generator: {str(e)}")

def save_generated_outfit(outfit_items, styling_tips, occasion, season, style):
    """Save a generated outfit to the user's collection"""
    outfits_file = f"{st.session_state.username}_outfits.json"
    
    try:
        # Load existing outfits
        if os.path.exists(outfits_file):
            with open(outfits_file, 'r') as f:
                outfits = json.load(f)
        else:
            outfits = []
        
        # Create new outfit entry
        new_outfit = {
            'name': f"{occasion} {style} Outfit",
            'items': outfit_items,
            'styling_tips': styling_tips,
            'occasion': occasion,
            'season': season,
            'style': style,
            'date_created': datetime.now().strftime("%Y-%m-%d")
        }
        
        outfits.append(new_outfit)
        
        # Save updated outfits
        with open(outfits_file, 'w') as f:
            json.dump(outfits, f, indent=4)
            
    except Exception as e:
        st.error(f"Error saving outfit: {str(e)}")

# Add the outfit generator to the main navigation
def main():
    st.sidebar.title("Outfit Manager")
    
    page = st.sidebar.selectbox(
        "Choose a function",
        ["Generate Outfit", "View Saved Outfits", "Schedule Outfits"]
    )
    
    if page == "Generate Outfit":
        display_outfit_generator()
    elif page == "View Saved Outfits":
        display_saved_outfits()
    elif page == "Schedule Outfits":
        schedule_outfits()

# ... rest of your existing code ... 