"""GPT-4 helper functions for generating structured responses"""

from openai import OpenAI
import os
from dotenv import load_dotenv

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