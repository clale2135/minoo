"""GPT-4 helper functions for generating structured responses"""

from openai import OpenAI
import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found in environment variables")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def gpt4_structured_response(prompt, system_role="You are a helpful assistant.", response_format=None):
    """Get a structured response from GPT-4"""
    try:
        messages = [
            {"role": "system", "content": system_role},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error getting GPT-4 response: {str(e)}")
        return None 

class ClothingItemResponse(BaseModel):
    name: str
    color: str
    type_of_clothing: str
    season: str
    occasion: str
    additional_details: str = ""

def gpt4o_structured_clothing(item_description: str):
    # Your GPT-4 clothing analysis code here
    pass

def analyze_style_preferences(responses):
    # Your style analysis code here
    pass

def suggest_weather_appropriate_outfit(weather_data, wardrobe):
    # Your weather outfit suggestion code here
    pass
