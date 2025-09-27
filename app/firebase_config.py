import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

def format_private_key(private_key):
    """Format the private key with proper headers and line breaks"""
    # Remove any existing headers, footers, and whitespace
    key = private_key.replace("-----BEGIN PRIVATE KEY-----", "")
    key = key.replace("-----END PRIVATE KEY-----", "")
    key = key.replace(" ", "")
    key = key.replace("\n", "")
    
    # Add header
    formatted_key = "-----BEGIN PRIVATE KEY-----\n"
    
    # Split the key into 64-character chunks
    chunks = [key[i:i+64] for i in range(0, len(key), 64)]
    
    # Join chunks with newlines
    formatted_key += "\n".join(chunks)
    
    # Add footer
    formatted_key += "\n-----END PRIVATE KEY-----\n"
    
    return formatted_key

def initialize_firebase():
    """Initialize Firebase with credentials"""
    try:
        # Debug: Print environment variables (without sensitive data)
        st.write("Checking Firebase configuration...")
        has_project_id = bool(os.getenv("FIREBASE_PROJECT_ID"))
        has_private_key = bool(os.getenv("FIREBASE_PRIVATE_KEY"))
        has_client_email = bool(os.getenv("FIREBASE_CLIENT_EMAIL"))
        
        st.write(f"""
        Firebase Configuration Status:
        - Project ID: {'✅' if has_project_id else '❌'}
        - Private Key: {'✅' if has_private_key else '❌'}
        - Client Email: {'✅' if has_client_email else '❌'}
        """)

        # Check if already initialized
        if not firebase_admin._apps:
            # Get and format the private key
            private_key = os.getenv("FIREBASE_PRIVATE_KEY", "")
            formatted_private_key = format_private_key(private_key)

            # Load credentials from environment variable
            cred_dict = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": formatted_private_key,
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
            }
            
            if not all(cred_dict.values()):
                missing_keys = [k for k, v in cred_dict.items() if not v]
                st.error(f"Missing Firebase credentials: {', '.join(missing_keys)}")
                return None
            
            try:
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                st.success("Firebase initialized successfully!")
            except Exception as e:
                st.error(f"Error initializing Firebase with credentials: {str(e)}")
                # Debug: Print the private key format
                st.write("Private key format:")
                st.write("- Starts with correct header:", formatted_private_key.startswith("-----BEGIN PRIVATE KEY-----"))
                st.write("- Ends with correct footer:", formatted_private_key.endswith("-----END PRIVATE KEY-----\n"))
                st.write("- Length:", len(formatted_private_key))
                st.write("- First few characters:", formatted_private_key[:50])
                return None
        
        return firestore.client()
    except Exception as e:
        st.error(f"Error in Firebase initialization: {str(e)}")
        return None 