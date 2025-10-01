from firebase_admin import firestore
import hashlib
from datetime import datetime

class FirebaseOps:
    def __init__(self, db):
        self.db = db
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, username, password):
        """Create a new user in Firebase"""
        try:
            users_ref = self.db.collection('users')
            # Check if username exists
            if users_ref.where('username', '==', username).get():
                return False, "Username already exists"
            
            # Create new user
            user_data = {
                'username': username,
                'password': self.hash_password(password),
                'created_at': datetime.now(),
                'last_login': datetime.now()
            }
            users_ref.add(user_data)
            return True, "User created successfully"
        except Exception as e:
            return False, f"Error creating user: {str(e)}"
    
    def verify_user(self, username, password):
        """Verify user credentials"""
        try:
            users_ref = self.db.collection('users')
            users = users_ref.where('username', '==', username).get()
            
            if not users:
                return False, "User not found"
            
            user = users[0]
            if user.to_dict()['password'] == self.hash_password(password):
                # Update last login
                user.reference.update({'last_login': datetime.now()})
                return True, user.id
            return False, "Invalid password"
        except Exception as e:
            return False, f"Error verifying user: {str(e)}"
    
    def save_clothing_item(self, user_id, item_data):
        """Save clothing item to user's wardrobe"""
        try:
            clothes_ref = self.db.collection('users').document(user_id).collection('wardrobe')
            clothes_ref.add({
                **item_data,
                'created_at': datetime.now()
            })
            return True, "Item saved successfully"
        except Exception as e:
            return False, f"Error saving item: {str(e)}"
    
    def get_user_wardrobe(self, user_id):
        """Get all clothing items for a user"""
        try:
            clothes_ref = self.db.collection('users').document(user_id).collection('wardrobe')
            clothes = clothes_ref.get()
            return [{'id': doc.id, **doc.to_dict()} for doc in clothes]
        except Exception as e:
            return []
    
    def save_outfit(self, user_id, outfit_data):
        """Save outfit to user's outfits"""
        try:
            outfits_ref = self.db.collection('users').document(user_id).collection('outfits')
            outfits_ref.add({
                **outfit_data,
                'created_at': datetime.now()
            })
            return True, "Outfit saved successfully"
        except Exception as e:
            return False, f"Error saving outfit: {str(e)}"
    
    def get_user_outfits(self, user_id):
        """Get all outfits for a user"""
        try:
            outfits_ref = self.db.collection('users').document(user_id).collection('outfits')
            outfits = outfits_ref.get()
            return [{'id': doc.id, **doc.to_dict()} for doc in outfits]
        except Exception as e:
            return [] 