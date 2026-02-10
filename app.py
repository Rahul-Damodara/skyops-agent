# Part of SkyOps Agent system – see README for architecture

"""
Streamlit frontend for SkyOps Agent.
This file contains no business logic.
"""

import streamlit as st
import pandas as pd
from agent.coordinator import run_agent
from agent.memory import agent_state

# Page configuration
st.set_page_config(
    page_title="SkyOps Agent - Drone Operations Coordinator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    st.header("📊 System Status")
    
    # Display agent state
    if agent_state.get('active_mission'):
        st.info(f"Active Mission: {agent_state['active_mission']}")
    else:
        st.success("No active mission")
    
    if agent_state.get('urgent_mode'):
        st.warning("🚨 **URGENT MODE ACTIVE**")
    else:
        st.success("✅ Normal operations")
    
    st.divider()
    
    st.header("ℹ️ About")
    st.markdown("""
    **SkyOps Agent** is an agentic AI system for drone operations.
    
    **Features:**
    - Query pilot, drone, and mission status
    - Assign pilots and drones to missions
    - Detect conflicts automatically
    - Urgent resource reassignment
    
    **Commands you can try:**
    - "Show me available pilots"
    - "List all drones"
    - "Assign Arjun to PRJ001 with Drone D001"
    - "What missions are active?"
    """)
    
    st.divider()
    
    if st.button("🔄 Clear Chat History"):
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

