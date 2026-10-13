import streamlit as st
import os
import base64
from app.database.schema import init_db

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Ontario Health AI Risk Directory",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Encode logo as base64 for CSS injection
logo_path = os.path.join(os.path.dirname(__file__), "app", "assets", "OH_logo.png")
with open(logo_path, "rb") as f:
    logo_b64 = base64.b64encode(f.read()).decode()

# Apply Ontario Health Design System Styling + Fixed Sidebar Logo
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Global Typography and Bright White Background */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
        }}
        
        .stApp {{
            background-color: #ffffff;
            color: #333333;
        }}
        
        /* Headers - OH Blue */
        h1, h2, h3, h4, h5, h6 {{
            color: #003865 !important;
            font-weight: 700 !important;
            letter-spacing: -0.01em;
        }}
        
        /* ====== SIDEBAR ====== */
        [data-testid="stSidebar"] {{
            background-color: #f8f9fa;
            border-right: 1px solid #e0e0e0;
        }}
        [data-testid="stSidebar"] * {{
            color: #333333 !important;
        }}
        
        /* Header bar with logo + project name */
        header[data-testid="stHeader"] {{
            background-color: rgba(255, 255, 255, 0.95);
            border-bottom: 1px solid #e0e0e0;
        }}
        header[data-testid="stHeader"]::before {{
            content: "";
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            width: 140px;
            height: 36px;
            background-image: url("data:image/png;base64,{logo_b64}");
            background-repeat: no-repeat;
            background-position: left center;
            background-size: contain;
            pointer-events: none;
        }}
        header[data-testid="stHeader"]::after {{
            content: "AI Initiatives Risk Directory";
            position: absolute;
            left: 50%;
            top: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 700;
            color: #003865;
            letter-spacing: 0.01em;
            pointer-events: none;
        }}
        
        /* Buttons - OH Blue */
        .stButton>button {{
            background-color: #0056b3;
            color: white !important;
            border-radius: 6px;
            border: none;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            transition: all 0.2s ease;
        }}
        .stButton>button:hover {{
            background-color: #003865;
            transform: translateY(-1px);
            box-shadow: 0 4px 10px rgba(0, 86, 179, 0.3);
        }}
        
        /* Input Fields - Highly Visible */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {{
            border-radius: 6px !important;
            border: 2px solid #cbd5e1 !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease;
        }}
        div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within, div[data-baseweb="select"] > div:focus-within {{
            border-color: #0056b3 !important;
            box-shadow: 0 0 0 3px rgba(0, 86, 179, 0.2) !important;
        }}
        
        /* Search Box placeholder */
        input::placeholder, textarea::placeholder {{
            color: #64748b !important;
            opacity: 1 !important;
            font-weight: 500;
        }}
        /* Forms */
        [data-testid="stForm"] {{
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }}
        
        /* Radio Buttons */
        div[data-testid="stRadio"] > label {{
            font-weight: 600 !important;
            color: #003865 !important;
            font-size: 14px !important;
        }}
        div[data-testid="stRadio"] div[role="radiogroup"] {{
            gap: 16px;
            padding: 4px 0;
        }}

        /* Prevent faded/washed-out look on disabled or read-only elements */
        input:disabled, textarea:disabled, [data-baseweb="input"] input:disabled, [data-baseweb="textarea"] textarea:disabled {{
            color: #0f172a !important;
            -webkit-text-fill-color: #0f172a !important;
            opacity: 1 !important;
            background-color: #f8fafc !important;
            border-color: #cbd5e1 !important;
            cursor: default !important;
            font-weight: 500 !important;
        }}

        /* Expanders styling */
        [data-testid="stExpander"] {{
            border: 1.5px solid #cbd5e1 !important;
            border-radius: 8px !important;
            background-color: #ffffff !important;
            margin-bottom: 12px !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.03) !important;
        }}
        [data-testid="stExpander"] summary {{
            font-weight: 600 !important;
            color: #003865 !important;
            font-size: 15px !important;
        }}

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 24px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 50px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 4px 4px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
        }}
        .stTabs [aria-selected="true"] {{
            border-bottom-color: #0056b3 !important;
            color: #0056b3 !important;
            font-weight: 700;
        }}
    </style>
""", unsafe_allow_html=True)

# Initialize Database
@st.cache_resource
def setup_database():
    init_db()
    
setup_database()

# Set up navigation
dashboard_page = st.Page("app/pages/dashboard.py", title="Dashboard", icon="📊", default=True)
projects_page = st.Page("app/pages/projects.py", title="Project Directory", icon="📁")
create_page = st.Page("app/pages/create_project.py", title="Create Project", icon="➕")
manage_page = st.Page("app/pages/manage_project.py", title="Manage Project", icon="⚙️")
admin_page = st.Page("app/pages/admin.py", title="Admin Console", icon="🔐")

pg = st.navigation({
    "Public Views": [dashboard_page, projects_page],
    "Project Owner": [create_page, manage_page],
    "Administration": [admin_page]
})



pg.run()

