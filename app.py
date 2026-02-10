"""
SkyOps Agent - Landing Page
Beautiful home page with statistics, features, and navigation
"""

import streamlit as st
from tools.sheets import get_sheet_data
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="SkyOps Agent - Drone Operations Coordinator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS with gradient and styling
st.markdown("""
    <style>
    /* Hero section styling */
    .hero-title {
        font-size: 4rem;
        font-weight: bold;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .hero-subtitle {
        font-size: 1.5rem;
        color: #666;
        text-align: center;
        margin-bottom: 3rem;
    }
    
    /* Stat card styling */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stat-number {
        font-size: 3rem;
        font-weight: bold;
        margin: 0;
    }
    .stat-label {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Feature card styling */
    .feature-card {
        background: #f0f2f6;
        padding: 2rem;
        border-radius: 1rem;
        height: 100%;
        transition: transform 0.2s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #1f1f1f;
        margin-bottom: 0.5rem;
    }
    .feature-card p {
        color: #333;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    </style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown('<h1 class="hero-title">🚁 SkyOps Agent</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">AI-Powered Drone Operations Coordinator</p>', unsafe_allow_html=True)

# Live Statistics Section
st.markdown("## 📊 Live System Statistics")

try:
    # Fetch live data from Google Sheets
    pilots_data = get_sheet_data(os.getenv('PILOT_RANGE', 'Pilot Roster!A2:H'))
    drones_data = get_sheet_data(os.getenv('DRONE_RANGE', 'Drone Fleet!A2:F'))
    missions_data = get_sheet_data(os.getenv('MISSION_RANGE', 'Missions!A2:I'))
    
    # Count available resources
    available_pilots = sum(1 for p in pilots_data if len(p) > 5 and p[5].lower() == 'available')
    available_drones = sum(1 for d in drones_data if len(d) > 2 and d[2].lower() == 'available')
    active_missions = len(missions_data)
    total_pilots = len(pilots_data)
    
    # Display stats in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{total_pilots}</p>
                <p class="stat-label">Total Pilots</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{available_pilots}</p>
                <p class="stat-label">Available Pilots</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{available_drones}</p>
                <p class="stat-label">Available Drones</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="stat-card">
                <p class="stat-number">{active_missions}</p>
                <p class="stat-label">Active Missions</p>
            </div>
        """, unsafe_allow_html=True)

except Exception as e:
    st.warning("⚠️ Could not fetch live statistics. Make sure Google Sheets is configured properly.")

st.divider()

# Key Features Section
st.markdown("## ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">Intelligent Agent</div>
            <p>Natural language interface powered by deterministic AI. Ask questions, make assignments, and manage operations conversationally.</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">⚡</div>
            <div class="feature-title">Real-Time Validation</div>
            <p>Automatic conflict detection prevents double-bookings and validates skills, certifications, and availability before any assignment.</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <div class="feature-title">Google Sheets Sync</div>
            <p>Bidirectional synchronization with Google Sheets. All changes reflect instantly, accessible to your entire team.</p>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col4, col5, col6 = st.columns(3)

with col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚨</div>
            <div class="feature-title">Urgent Reassignments</div>
            <p>Handle emergency situations with urgent reassignment workflow. Quickly move resources between missions when priorities change.</p>
        </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <div class="feature-title">Smart Suggestions</div>
            <p>When assignments fail, get intelligent recommendations for alternative pilots and drones with match scores and explanations.</p>
        </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Analytics Dashboard</div>
            <p>Comprehensive statistics, capacity planning, and operational insights. Monitor utilization and identify bottlenecks at a glance.</p>
        </div>
    """, unsafe_allow_html=True)

st.divider()

# Get Started Section
st.markdown("## 🚀 Get Started")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 💬 Chat Interface")
    st.markdown("Talk to the agent using natural language commands")
    st.page_link("pages/1__Chat.py", label="Open Chat", icon="💬", use_container_width=True)

with col2:
    st.markdown("### 📊 Statistics")
    st.markdown("View real-time analytics and operational insights")
    st.page_link("pages/2_📊_Analytics.py", label="View Statistics", icon="📊", use_container_width=True)

with col3:
    st.markdown("### ➕ Add Resources")
    st.markdown("Add new pilots, drones, or missions to the system")
    st.page_link("pages/3_➕_Add_Resources.py", label="Add Resources", icon="➕", use_container_width=True)

st.divider()

# How it Works Section
st.markdown("## 🔧 How It Works")

tab1, tab2, tab3 = st.tabs(["🎯 Architecture", "📝 Example Commands", "🔐 Safety"])

with tab1:
    st.markdown("""
    ### Deterministic AI Architecture
    
    ```
    User Input (Natural Language)
           ↓
    Intent Parser (LLM + Keyword Fallback)
           ↓
    Planner (Converts Intent → Action Steps)
           ↓
    Rules Engine (Validates All Constraints)
           ↓
    Executor (Updates Google Sheets)
           ↓
    Response (User-Friendly Message + Data)
    ```
    
    **Why Deterministic?**
    - ✅ Zero risk of hallucinated assignments
    - ✅ Complete audit trail of all decisions
    - ✅ Predictable behavior for testing
    - ✅ Works even if LLM is unavailable (keyword fallback)
    
    **LLM Role:** Only for parsing user input, never for operational decisions
    """)

with tab2:
    st.markdown("""
    ### Try These Commands
    
    **Query Operations:**
    - "Show me all available pilots"
    - "List drones in maintenance"
    - "What missions are in Bangalore?"
    - "Is Arjun available?"
    
    **Assignment Operations:**
    - "Assign Sneha to PRJ002 with Drone D005"
    - "Allocate pilot P001 and drone D003 to PRJ010"
    - "Schedule Rohit for Mission PRJ015 with D008"
    
    **Management Operations:**
    - "Remove Arjun from PRJ001"
    - "Urgent: Move D001 from PRJ003 to PRJ007"
    - "Add new pilot named Priya with Mapping skills"
    
    **Status Checks:**
    - "Show pilot roster"
    - "Check drone D001 status"
    - "What's assigned to PRJ005?"
    """)

with tab3:
    st.markdown("""
    ### Safety & Validation
    
    **🛡️ Hard Blockers (Assignment Fails):**
    1. Pilot already assigned to another mission
    2. Drone already assigned to another mission
    3. Pilot missing required skills
    4. Pilot missing required certifications
    5. Drone in maintenance
    6. Mission dates conflict with availability
    7. Double-booking detected
    
    **⚠️ Soft Warnings (Shows Warning but Allows):**
    1. Location mismatch (pilot/drone can travel)
    2. Availability date after mission start
    
    **🔒 Data Integrity:**
    - All operations are atomic (all-or-nothing)
    - Google Sheets updated only after validation passes
    - Audit trail of all changes
    - Suggestions provided when assignments fail
    """)

st.divider()

# Footer
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem 0;'>
    <strong>SkyOps Agent</strong> — Deterministic AI for Drone Operations<br>
    Built for <a href='https://github.com/Rahul-Damodara/skyops-agent' target='_blank'>Skylark Drones Technical Assignment</a> | 
    <a href='https://github.com/Rahul-Damodara/skyops-agent' target='_blank'>View on GitHub</a>
</div>
""", unsafe_allow_html=True)

