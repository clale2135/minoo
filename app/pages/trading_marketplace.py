import streamlit as st
from PIL import Image
import pandas as pd
import json
import os
import uuid
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Trading Marketplace",
    page_icon="🔄",
    layout="wide"
)

# Check authentication
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please log in to access the Trading Marketplace.")
    st.stop()

def load_user_clothing():
    """Load user's clothing data"""
    user_file = f"{st.session_state.username}_clothing.csv"
    if os.path.exists(user_file):
        return pd.read_csv(user_file)
    return pd.DataFrame(columns=["id", "name", "color", "type_of_clothing", "season", "occasion", "image_path"])

def create_trade_listing():
    """Create a new trade listing for a clothing item"""
    st.title("📊 Create Trade Listing")
    
    # Load user's clothing
    user_clothing = load_user_clothing()
    
    if user_clothing.empty:
        st.warning("You need to add clothes to your wardrobe first!")
        return
    
    with st.form("trade_listing_form"):
        # Select item to trade
        available_items = user_clothing['name'].tolist()
        item_to_trade = st.selectbox(
            "Select item to trade",
            available_items
        )
        
        # Get item details
        item_details = user_clothing[user_clothing['name'] == item_to_trade].iloc[0]
        
        # Display item image
        if os.path.exists(item_details['image_path']):
            image = Image.open(item_details['image_path'])
            st.image(image, caption=item_to_trade, width=200)
        
        # Trade preferences
        st.markdown("### Trade Preferences")
        
        desired_types = st.multiselect(
            "What types of clothing would you accept in trade?",
            ["Shirt", "Pants", "Jacket", "Dress", "Skirt", "Shorts", "Sweater", 
             "T-shirt", "Blouse", "Coat", "Jeans", "Shoes"],
            default=[item_details['type_of_clothing']]
        )
        
        condition = st.select_slider(
            "Item Condition",
            options=["Like New", "Gently Used", "Well Worn", "Vintage"],
            value="Gently Used"
        )
        
        description = st.text_area(
            "Additional Description",
            placeholder="Add any details about the item or your trade preferences..."
        )
        
        # Submit button
        if st.form_submit_button("Create Listing"):
            create_listing_in_db(
                username=st.session_state.username,
                item_name=item_to_trade,
                item_details=item_details,
                desired_types=desired_types,
                condition=condition,
                description=description
            )
            st.success("Listing created successfully!")
            time.sleep(1)
            st.rerun()

def create_listing_in_db(username, item_name, item_details, desired_types, condition, description):
    """Save trade listing to database"""
    listing = {
        "id": str(uuid.uuid4()),
        "username": username,
        "item_name": item_name,
        "image_path": item_details['image_path'],
        "type_of_clothing": item_details['type_of_clothing'],
        "desired_types": desired_types,
        "condition": condition,
        "description": description,
        "status": "active",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    listings_file = "trade_listings.json"
    
    try:
        if os.path.exists(listings_file):
            with open(listings_file, 'r') as f:
                listings = json.load(f)
        else:
            listings = []
        
        listings.append(listing)
        
        with open(listings_file, 'w') as f:
            json.dump(listings, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving listing: {str(e)}")

def browse_trade_listings():
    """Browse and filter available trade listings"""
    st.title("🔄 Trade Marketplace")
    
    # Load all listings
    listings_file = "trade_listings.json"
    if not os.path.exists(listings_file):
        st.info("No trade listings available yet!")
        return
        
    try:
        with open(listings_file, 'r') as f:
            listings = json.load(f)
    except Exception as e:
        st.error(f"Error loading listings: {str(e)}")
        return
    
    # Filter active listings and exclude user's own listings
    active_listings = [
        l for l in listings 
        if l['status'] == 'active' and l['username'] != st.session_state.username
    ]
    
    if not active_listings:
        st.info("No active listings available!")
        return
    
    # Filtering options
    st.markdown("### Filter Listings")
    col1, col2 = st.columns(2)
    
    with col1:
        selected_types = st.multiselect(
            "Clothing Types",
            list(set(l['type_of_clothing'] for l in active_listings))
        )
    
    with col2:
        selected_condition = st.multiselect(
            "Condition",
            ["Like New", "Gently Used", "Well Worn", "Vintage"]
        )
    
    # Apply filters
    filtered_listings = active_listings
    if selected_types:
        filtered_listings = [l for l in filtered_listings if l['type_of_clothing'] in selected_types]
    if selected_condition:
        filtered_listings = [l for l in filtered_listings if l['condition'] in selected_condition]
    
    # Display listings in grid
    st.markdown("### Available Items")
    
    for i in range(0, len(filtered_listings), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            if i + j < len(filtered_listings):
                listing = filtered_listings[i + j]
                with col:
                    st.subheader(listing['item_name'])
                    
                    if os.path.exists(listing['image_path']):
                        image = Image.open(listing['image_path'])
                        st.image(image, use_column_width=True)
                    
                    st.markdown(f"**Type:** {listing['type_of_clothing']}")
                    st.markdown(f"**Condition:** {listing['condition']}")
                    st.markdown(f"**Looking for:** {', '.join(listing['desired_types'])}")
                    
                    if st.button(f"Propose Trade", key=f"trade_{listing['id']}"):
                        propose_trade(listing)

def propose_trade(listing):
    """Interface for proposing a trade"""
    st.session_state.proposing_trade = True
    st.session_state.selected_listing = listing
    
    # Load user's clothing
    user_clothing = load_user_clothing()
    
    # Filter items that match desired types
    matching_items = user_clothing[
        user_clothing['type_of_clothing'].isin(listing['desired_types'])
    ]
    
    if matching_items.empty:
        st.warning("You don't have any items that match the desired types!")
        return
    
    st.markdown("### Propose Trade")
    st.markdown(f"Trading with: **{listing['username']}**")
    
    # Select item to trade
    item_to_trade = st.selectbox(
        "Select your item to trade",
        matching_items['name'].tolist()
    )
    
    # Add message
    message = st.text_area(
        "Add a message (optional)",
        placeholder="Explain why this would be a good trade..."
    )
    
    if st.button("Send Trade Proposal"):
        create_trade_proposal(
            listing_id=listing['id'],
            proposer_username=st.session_state.username,
            proposed_item_name=item_to_trade,
            message=message
        )
        st.success("Trade proposal sent!")
        time.sleep(1)
        st.rerun()

def create_trade_proposal(listing_id, proposer_username, proposed_item_name, message):
    """Save trade proposal to database"""
    proposal = {
        "id": str(uuid.uuid4()),
        "listing_id": listing_id,
        "proposer_username": proposer_username,
        "proposed_item_name": proposed_item_name,
        "message": message,
        "status": "pending",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    proposals_file = "trade_proposals.json"
    
    try:
        if os.path.exists(proposals_file):
            with open(proposals_file, 'r') as f:
                proposals = json.load(f)
        else:
            proposals = []
        
        proposals.append(proposal)
        
        with open(proposals_file, 'w') as f:
            json.dump(proposals, f, indent=2)
            
    except Exception as e:
        st.error(f"Error saving proposal: {str(e)}")

def view_trade_proposals():
    """View and manage trade proposals"""
    st.title("📫 Trade Proposals")
    
    # Load proposals
    proposals_file = "trade_proposals.json"
    if not os.path.exists(proposals_file):
        st.info("No trade proposals yet!")
        return
        
    try:
        with open(proposals_file, 'r') as f:
            proposals = json.load(f)
    except Exception as e:
        st.error(f"Error loading proposals: {str(e)}")
        return
    
    # Load listings
    with open("trade_listings.json", 'r') as f:
        listings = json.load(f)
    
    # Separate received and sent proposals
    received_proposals = [
        p for p in proposals 
        if any(
            l['username'] == st.session_state.username and l['id'] == p['listing_id']
            for l in listings
        )
    ]
    
    sent_proposals = [
        p for p in proposals 
        if p['proposer_username'] == st.session_state.username
    ]
    
    # Display proposals in tabs
    tab1, tab2 = st.tabs(["Received Proposals", "Sent Proposals"])
    
    with tab1:
        if not received_proposals:
            st.info("No received proposals!")
        else:
            for proposal in received_proposals:
                listing = next(l for l in listings if l['id'] == proposal['listing_id'])
                
                st.markdown(f"""
                    <div style='
                        background-color: white;
                        padding: 1.5rem;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                    '>
                        <h4>Trade Proposal for {listing['item_name']}</h4>
                        <p><strong>From:</strong> {proposal['proposer_username']}</p>
                        <p><strong>Offering:</strong> {proposal['proposed_item_name']}</p>
                        <p><strong>Message:</strong> {proposal['message']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Accept", key=f"accept_{proposal['id']}"):
                        accept_trade_proposal(proposal, listing)
                with col2:
                    if st.button("Decline", key=f"decline_{proposal['id']}"):
                        decline_trade_proposal(proposal)
    
    with tab2:
        if not sent_proposals:
            st.info("No sent proposals!")
        else:
            for proposal in sent_proposals:
                listing = next(l for l in listings if l['id'] == proposal['listing_id'])
                
                st.markdown(f"""
                    <div style='
                        background-color: white;
                        padding: 1.5rem;
                        border-radius: 10px;
                        margin-bottom: 1rem;
                    '>
                        <h4>Proposal for {listing['item_name']}</h4>
                        <p><strong>Status:</strong> {proposal['status'].title()}</p>
                        <p><strong>Your offer:</strong> {proposal['proposed_item_name']}</p>
                    </div>
                """, unsafe_allow_html=True)

def accept_trade_proposal(proposal, listing):
    """Process accepted trade proposal"""
    # Update proposal status
    update_proposal_status(proposal['id'], "accepted")
    
    # Update listing status
    update_listing_status(listing['id'], "completed")
    
    # Transfer items between users
    transfer_items(
        from_username=listing['username'],
        to_username=proposal['proposer_username'],
        item_name=listing['item_name']
    )
    
    transfer_items(
        from_username=proposal['proposer_username'],
        to_username=listing['username'],
        item_name=proposal['proposed_item_name']
    )
    
    st.success("Trade completed successfully!")
    time.sleep(1)
    st.rerun()

def decline_trade_proposal(proposal):
    """Process declined trade proposal"""
    update_proposal_status(proposal['id'], "declined")
    st.success("Proposal declined")
    time.sleep(1)
    st.rerun()

def update_proposal_status(proposal_id, new_status):
    """Update status of a trade proposal"""
    proposals_file = "trade_proposals.json"
    
    with open(proposals_file, 'r') as f:
        proposals = json.load(f)
    
    for proposal in proposals:
        if proposal['id'] == proposal_id:
            proposal['status'] = new_status
            break
    
    with open(proposals_file, 'w') as f:
        json.dump(proposals, f, indent=2)

def update_listing_status(listing_id, new_status):
    """Update status of a trade listing"""
    listings_file = "trade_listings.json"
    
    with open(listings_file, 'r') as f:
        listings = json.load(f)
    
    for listing in listings:
        if listing['id'] == listing_id:
            listing['status'] = new_status
            break
    
    with open(listings_file, 'w') as f:
        json.dump(listings, f, indent=2)

def transfer_items(from_username, to_username, item_name):
    """Transfer item between users"""
    # Load both users' clothing data
    from_user_file = f"{from_username}_clothing.csv"
    to_user_file = f"{to_username}_clothing.csv"
    
    from_clothing = pd.read_csv(from_user_file)
    to_clothing = pd.read_csv(to_user_file)
    
    # Get item details
    item_details = from_clothing[from_clothing['name'] == item_name].iloc[0]
    
    # Remove from original user
    from_clothing = from_clothing[from_clothing['name'] != item_name]
    
    # Add to new user
    to_clothing = pd.concat([to_clothing, pd.DataFrame([item_details])], ignore_index=True)
    
    # Save updated data
    from_clothing.to_csv(from_user_file, index=False)
    to_clothing.to_csv(to_user_file, index=False)

# Main interface
tab1, tab2, tab3 = st.tabs(["Browse Listings", "Create Listing", "Trade Proposals"])

with tab1:
    browse_trade_listings()

with tab2:
    create_trade_listing()

with tab3:
    view_trade_proposals() 