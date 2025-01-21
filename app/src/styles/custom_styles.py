def set_custom_style():
    """Set custom styling for a luxury boutique theme"""
    return """
        <style>
        /* Luxury Boutique Theme */
        :root {
            --champagne-gold: #AD9B6C;
            --soft-gold: #D4AF37;
            --cream: #FFFBF4;
            --charcoal: #2C3E50;
            --taupe: #8B7355;
            --ivory: #FFFFF0;
            --muted-gold: rgba(173, 155, 108, 0.1);
            --shadow: rgba(0, 0, 0, 0.05);
            --text-primary: #000000;  /* Added for consistent text color */
        }

        /* Ensure all text is visible */
        .stMarkdown, 
        .stText, 
        p, 
        span, 
        label, 
        div {
            color: var(--text-primary) !important;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6, .stTitle {
            color: var(--charcoal) !important;
        }

        /* Input text */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div {
            color: var(--text-primary) !important;
        }

        /* Selectbox text */
        .stSelectbox > div,
        .stSelectbox span {
            color: var(--text-primary) !important;
        }

        /* Multiselect text */
        .stMultiSelect > div,
        .stMultiSelect span:not([data-baseweb="tag"]) {
            color: var(--text-primary) !important;
        }

        /* Radio buttons and checkboxes */
        .stRadio label,
        .stCheckbox label {
            color: var(--text-primary) !important;
        }

        /* Metrics */
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"] {
            color: var(--text-primary) !important;
        }

        /* Sidebar - keep white text on dark background */
        [data-testid="stSidebar"] {
            background-color: #1a1a1a;
        }

        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] .stSelectbox > div {
            color: white !important;
        }

        /* Ensure dropdown menu text is visible */
        [role="listbox"] [role="option"] {
            color: var(--text-primary) !important;
        }

        /* Table text */
        .dataframe td,
        .dataframe th {
            color: var(--text-primary) !important;
        }

        /* Button text - keep white for contrast */
        .stButton > button {
            color: white !important;
        }

        /* Toast notifications */
        .stToast {
            color: var(--text-primary) !important;
        }

        /* Error and warning messages */
        .stAlert {
            color: var(--text-primary) !important;
        }

        /* Keep white text in dark-themed elements */
        [data-baseweb="tag"] {
            color: white !important;
        }

        /* Ensure form labels are visible */
        .stForm label {
            color: var(--text-primary) !important;
        }

        /* Ensure tooltips are visible */
        .stTooltipIcon {
            color: var(--champagne-gold) !important;
        }

        /* Ensure links are visible */
        a {
            color: var(--champagne-gold) !important;
        }

        /* Ensure placeholder text is visible */
        ::placeholder {
            color: #666666 !important;
            opacity: 1 !important;
        }

        /* Main container styling */
        .stApp {
            background: linear-gradient(
                135deg, 
                var(--cream) 0%, 
                var(--ivory) 100%
            );
        }

        /* Card and container styling */
        .stMarkdown, .stButton, .stSelectbox, .stTextInput {
            font-family: 'Cormorant Garamond', 'Playfair Display', serif;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(
                135deg, 
                var(--champagne-gold) 0%, 
                var(--soft-gold) 100%
            );
            color: var(--ivory);
            border: none;
            padding: 0.8rem 1.5rem;
            border-radius: 4px;
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            font-size: 0.9rem;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px var(--shadow);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(173, 155, 108, 0.2);
            background: linear-gradient(
                135deg, 
                var(--soft-gold) 0%, 
                var(--champagne-gold) 100%
            );
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #1a1a1a;
            border-right: 1px solid var(--champagne-gold);
            box-shadow: 2px 0 20px var(--shadow);
        }

        /* Input fields */
        .stTextInput > div > div > input {
            background-color: var(--ivory);
            border: 1px solid var(--champagne-gold);
            border-radius: 4px;
            padding: 1rem;
            transition: all 0.3s ease;
        }

        .stTextInput > div > div > input:focus {
            border-color: var(--soft-gold);
            box-shadow: 0 0 0 2px rgba(173, 155, 108, 0.2);
        }

        /* Select boxes */
        .stSelectbox > div > div {
            background-color: var(--ivory);
            border: 1px solid var(--champagne-gold);
            border-radius: 4px;
        }

        /* Cards for clothing items */
        .clothes-card {
            background-color: var(--ivory);
            border-radius: 8px;
            padding: 2rem;
            box-shadow: 0 4px 20px var(--shadow);
            border: 1px solid var(--champagne-gold);
            transition: all 0.3s ease;
        }

        .clothes-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px var(--shadow);
        }

        /* Images */
        .stImage {
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px var(--shadow);
        }

        /* Success messages */
        .stSuccess {
            background-color: rgba(173, 155, 108, 0.1);
            color: var(--charcoal);
            border-left: 4px solid var(--champagne-gold);
        }

        /* Error messages */
        .stError {
            background-color: #FBE9E7;
            color: var(--charcoal);
            border-left: 4px solid #C62828;
        }

        /* Welcome message */
        .welcome-msg {
            color: var(--charcoal);
            text-align: center;
            padding: 3rem;
            margin: 2rem 0;
            font-size: 1.3rem;
            line-height: 1.8;
            font-family: 'Cormorant Garamond', serif;
            background: var(--muted-gold);
            border-radius: 8px;
            border: 1px solid var(--champagne-gold);
        }

        /* Tables */
        .dataframe {
            border: 1px solid var(--champagne-gold);
            border-radius: 8px;
            overflow: hidden;
            background: var(--ivory);
            box-shadow: 0 4px 20px var(--shadow);
        }

        .dataframe th {
            background-color: var(--muted-gold);
            color: var(--charcoal);
            font-weight: 600;
            padding: 1rem;
            border-bottom: 2px solid var(--champagne-gold);
        }

        /* Tooltips */
        .stTooltipIcon {
            color: var(--champagne-gold) !important;
        }

        /* Sidebar navigation styling */
        .stSidebar {
            background-color: #2c3e50;
        }
        
        /* Make all text in sidebar white */
        .stSidebar [data-testid="stSidebarNav"] {
            color: white !important;
        }
        
        .stSidebar [data-testid="stSidebarNav"] a {
            color: white !important;
        }
        
        /* Selectbox in sidebar */
        .stSidebar .stSelectbox label {
            color: white !important;
        }
        
        .stSidebar .stSelectbox div[data-baseweb="select"] {
            color: white !important;
        }
        
        /* Dropdown items */
        .stSidebar .stSelectbox ul {
            background-color: #2c3e50 !important;
        }
        
        .stSidebar .stSelectbox ul li {
            color: white !important;
        }
        
        /* Buttons in sidebar */
        .stSidebar button {
            color: white !important;
        }
        
        /* All text elements in sidebar */
        .stSidebar p, .stSidebar span, .stSidebar div {
            color: white !important;
        }
        
        /* Navigation links hover state */
        .stSidebar [data-testid="stSidebarNav"] a:hover {
            background-color: #34495e !important;
            color: white !important;
        }
        
        /* Active/selected navigation item */
        .stSidebar [data-testid="stSidebarNav"] li[aria-selected="true"] {
            background-color: #34495e !important;
        }

        /* Force all sidebar elements to be white */
        section[data-testid="stSidebar"] {
            background-color: #2c3e50;
        }
        
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
        
        /* Specific styling for navigation items */
        .st-emotion-cache-16idsys p,
        .st-emotion-cache-16idsys span,
        .st-emotion-cache-16idsys div,
        .st-emotion-cache-16idsys a,
        .st-emotion-cache-16idsys button {
            color: white !important;
        }
        
        /* Dropdown/Select boxes */
        section[data-testid="stSidebar"] select,
        section[data-testid="stSidebar"] .stSelectbox label,
        section[data-testid="stSidebar"] .stSelectbox span {
            color: white !important;
        }
        
        /* Hover states */
        section[data-testid="stSidebar"] a:hover,
        section[data-testid="stSidebar"] button:hover {
            background-color: #34495e !important;
            color: white !important;
        }
        
        /* Selected/active states */
        section[data-testid="stSidebar"] [aria-selected="true"] {
            background-color: #34495e !important;
        }
        
        /* Authentication section */
        section[data-testid="stSidebar"] .block-container {
            color: white !important;
        }

        /* Main sidebar container */
        [data-testid="stSidebar"] {
            background-color: #1a1a1a;
        }
        
        /* Sidebar navigation items */
        [data-testid="stSidebar"] .st-emotion-cache-6qob1r {
            background-color: #1a1a1a;
            color: #ffffff !important;
        }
        
        /* Sidebar navigation text */
        [data-testid="stSidebar"] .st-emotion-cache-16idsys {
            color: #ffffff !important;
        }
        
        /* Sidebar links */
        [data-testid="stSidebar"] a {
            color: #ffffff !important;
        }
        
        /* Hover state for navigation items */
        [data-testid="stSidebar"] .st-emotion-cache-16idsys:hover {
            background-color: #333333 !important;
            color: #ffffff !important;
        }
        
        /* Selected/active navigation item */
        [data-testid="stSidebar"] [aria-selected="true"] {
            background-color: #333333 !important;
        }
        
        /* Selectbox/Dropdown styling */
        [data-testid="stSidebar"] .stSelectbox label {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
            background-color: #333333 !important;
            color: #ffffff !important;
        }
        
        /* Buttons in sidebar */
        [data-testid="stSidebar"] button {
            background-color: #333333 !important;
            color: #ffffff !important;
            border: 1px solid #4d4d4d !important;
        }
        
        [data-testid="stSidebar"] button:hover {
            background-color: #4d4d4d !important;
            border-color: #666666 !important;
        }
        
        /* All text elements in sidebar */
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span, 
        [data-testid="stSidebar"] div {
            color: #ffffff !important;
        }
        
        /* Dropdown menu items */
        [data-testid="stSidebar"] ul {
            background-color: #1a1a1a !important;
        }
        
        [data-testid="stSidebar"] li {
            color: #ffffff !important;
        }
        
        [data-testid="stSidebar"] li:hover {
            background-color: #333333 !important;
        }
        </style>
    """ 