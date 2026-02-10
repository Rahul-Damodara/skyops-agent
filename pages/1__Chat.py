# Part of SkyOps Agent system – see README for architecture

"""
Chat Interface - Interact with SkyOps Agent
"""

import streamlit as st
import pandas as pd
from agent.coordinator import run_agent
from agent.memory import agent_state

# Page configuration
st.set_page_config(
    page_title="Chat - SkyOps Agent",
    page_icon="💬",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header">🚁 SkyOps Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Intelligent Drone Operations Coordinator</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    use_llm = st.checkbox(
        "Use LLM for Intent Parsing",
        value=False,
        help="Enable to use OpenAI/Anthropic for better intent understanding. Disable for simple keyword-based parsing."
    )
    
    st.divider()
    
    st.header("📊 Quick Stats")
    
    # Load real-time data for sidebar
    try:
        from tools.sheets import get_sheet_as_df
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        pilot_range = os.getenv('PILOT_RANGE')
        drone_range = os.getenv('DRONE_RANGE')
        mission_range = os.getenv('MISSION_RANGE')
        
        pilots_df = get_sheet_as_df(spreadsheet_id, pilot_range)
        drones_df = get_sheet_as_df(spreadsheet_id, drone_range)
        missions_df = get_sheet_as_df(spreadsheet_id, mission_range)
        
        # Calculate stats
        total_pilots = len(pilots_df)
        available_pilots = len(pilots_df[pilots_df['status'].str.lower() == 'available']) if 'status' in pilots_df.columns else 0
        
        total_drones = len(drones_df)
        available_drones = len(drones_df[drones_df['status'].str.lower() == 'available']) if 'status' in drones_df.columns else 0
        
        total_missions = len(missions_df)
        
        # Display metrics
        col1, col2 = st.columns(2)
        with col1:
            st.metric("👨‍✈️ Pilots", total_pilots, f"{available_pilots} free")
        with col2:
            st.metric("🚁 Drones", total_drones, f"{available_drones} free")
        
        st.metric("📦 Missions", total_missions)
        
        # System health
        if available_pilots > 0 and available_drones > 0:
            st.success("✅ System Operational")
        elif available_pilots == 0:
            st.warning("⚠️ No Available Pilots")
        elif available_drones == 0:
            st.warning("⚠️ No Available Drones")
            
    except Exception as e:
        st.info("Unable to load live stats")
    
    st.divider()
    
    st.header("💬 Quick Commands")
    st.markdown("""
    **Query:**
    - "Show available pilots"
    - "List all drones"
    - "What missions are active?"
    
    **Assign:**
    - "Assign [Pilot] to [Mission] with Drone [ID]"
    
    **Urgent:**
    - "Urgent: Move [Drone] from [Mission1] to [Mission2]"
    """)
    
    st.divider()
    
    if st.button("🔄 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display data if present
        if "data" in message and message["data"]:
            data = message["data"]
            
            # Display pilots
            if "pilots" in data and data["pilots"]:
                with st.expander("📋 Pilot Details"):
                    st.dataframe(pd.DataFrame(data["pilots"]), use_container_width=True)
            
            # Display drones
            if "drones" in data and data["drones"]:
                with st.expander("🚁 Drone Details"):
                    st.dataframe(pd.DataFrame(data["drones"]), use_container_width=True)
            
            # Display missions
            if "missions" in data and data["missions"]:
                with st.expander("📦 Mission Details"):
                    st.dataframe(pd.DataFrame(data["missions"]), use_container_width=True)
            
            # Display validation warnings
            if "warnings" in data and data["warnings"]:
                with st.expander("⚠️ Warnings"):
                    for warning in data["warnings"]:
                        st.warning(warning)

# Chat input
if prompt := st.chat_input("What would you like to do?"):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Process with agent
    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # Run the agent
            result = run_agent(prompt, use_llm=use_llm)
            
            # Display the response
            if result['success']:
                st.success(result['message'])
            else:
                st.error(result['message'])
            
            # Store assistant message
            assistant_message = {
                "role": "assistant",
                "content": result['message']
            }
            
            # Add data if present
            if result.get('data'):
                assistant_message["data"] = result['data']
                
                # Display data immediately
                data = result['data']
                
                if "pilots" in data and data["pilots"]:
                    with st.expander("📋 Pilot Details", expanded=True):
                        st.dataframe(pd.DataFrame(data["pilots"]), use_container_width=True)
                
                if "drones" in data and data["drones"]:
                    with st.expander("🚁 Drone Details", expanded=True):
                        st.dataframe(pd.DataFrame(data["drones"]), use_container_width=True)
                
                if "missions" in data and data["missions"]:
                    with st.expander("📦 Mission Details", expanded=True):
                        st.dataframe(pd.DataFrame(data["missions"]), use_container_width=True)
                
                if "warnings" in data and data["warnings"]:
                    with st.expander("⚠️ Warnings"):
                        for warning in data["warnings"]:
                            st.warning(warning)
            
            # Show execution steps in expander
            if result.get('steps_taken'):
                with st.expander("🔍 Execution Steps"):
                    for i, step in enumerate(result['steps_taken'], 1):
                        st.text(f"{i}. {step}")
            
            st.session_state.messages.append(assistant_message)

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <strong>SkyOps Agent</strong> | Deterministic AI for Drone Operations | 
    <a href='https://github.com/Rahul-Damodara/skyops-agent' target='_blank'>GitHub</a>
</div>
""", unsafe_allow_html=True)

