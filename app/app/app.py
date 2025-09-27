import streamlit as st

# This must be the first Streamlit command - before any other imports or code
st.set_page_config(
    page_title="Digital Wardrobe",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now continue with your other imports and code
import os
import json
import time
from datetime import datetime, timedelta
from PIL import Image
import io
import requests
import pyperclip
# ... rest of your imports ...

# ... rest of your code ...