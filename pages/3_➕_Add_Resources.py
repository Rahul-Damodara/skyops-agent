# Part of SkyOps Agent system – see README for architecture

"""
Add Resources page - Add new pilots, drones, or missions
"""

import streamlit as st
import pandas as pd
from tools.pilots import add_new_pilot
from tools.drones import add_new_drone
from tools.missions import add_new_mission
from tools.sheets import get_sheet_as_df
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Add Resources - SkyOps Agent",
    page_icon="➕",
    layout="wide"
)

# Header
st.markdown('<div style="text-align: center;"><h1>➕ Add New Resources</h1></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">Add new pilots, drones, or missions to the system</div>', unsafe_allow_html=True)

st.divider()

# Tabs for different resource types
tab1, tab2, tab3 = st.tabs(["👨‍✈️ Add Pilot", "🚁 Add Drone", "📦 Add Mission"])

# --- ADD PILOT ---
with tab1:
    st.subheader("Add New Pilot to Roster")
    
    with st.form("add_pilot_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            pilot_name = st.text_input("Name *", placeholder="e.g., Rajesh Kumar")
            pilot_skills = st.text_input("Skills *", placeholder="e.g., Mapping, Survey, Inspection")
            pilot_certs = st.text_input("Certifications *", placeholder="e.g., DGCA, Night Ops")
            pilot_location = st.text_input("Location *", placeholder="e.g., Bangalore")
        
        with col2:
            pilot_contact = st.text_input("Contact", placeholder="e.g., +91 9876543210")
            pilot_experience = st.number_input("Experience (years)", min_value=0, max_value=50, value=5)
            pilot_status = st.selectbox("Status", ["Available", "Assigned", "Inactive"])
            pilot_available_from = st.date_input("Available From")
        
        submit_pilot = st.form_submit_button("➕ Add Pilot", use_container_width=True, type="primary")
        
        if submit_pilot:
            if not pilot_name or not pilot_skills or not pilot_certs or not pilot_location:
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    with st.spinner("Adding pilot to roster..."):
                        pilot_data = {
                            'name': pilot_name,
                            'skills': pilot_skills,
                            'certifications': pilot_certs,
                            'location': pilot_location,
                            'contact': pilot_contact if pilot_contact else 'N/A',
                            'experience_years': str(pilot_experience),
                            'status': pilot_status,
                            'available_from': pilot_available_from.strftime('%d-%m-%Y'),
                            'current_assignment': '–'
                        }
                        
                        result = add_new_pilot(pilot_data)
                        
                        if result.get('success'):
                            st.success(f"✅ Pilot added successfully with ID: {result.get('pilot_id')}")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"❌ Error adding pilot: {str(e)}")
    
    # Show existing pilots
    with st.expander("📋 View Existing Pilots"):
        try:
            spreadsheet_id = os.getenv('SPREADSHEET_ID')
            pilot_range = os.getenv('PILOT_RANGE')
            pilots_df = get_sheet_as_df(spreadsheet_id, pilot_range)
            st.dataframe(pilots_df, use_container_width=True, height=300)
            st.info(f"Total Pilots: {len(pilots_df)}")
        except Exception as e:
            st.error(f"Unable to load existing pilots: {str(e)}")

# --- ADD DRONE ---
with tab2:
    st.subheader("Add New Drone to Fleet")
    
    with st.form("add_drone_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            drone_model = st.text_input("Model *", placeholder="e.g., DJI M300")
            drone_capabilities = st.text_input("Capabilities *", placeholder="e.g., LiDAR, RGB, Thermal")
            drone_status = st.selectbox("Status", ["Available", "Assigned", "Maintenance"], key="drone_status")
            drone_location = st.text_input("Location *", placeholder="e.g., Delhi", key="drone_location")
        
        with col2:
            drone_payload = st.number_input("Payload Capacity (kg)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
            drone_battery = st.slider("Battery Status (%)", min_value=0, max_value=100, value=100)
            drone_maintenance_due = st.date_input("Maintenance Due Date")
        
        submit_drone = st.form_submit_button("➕ Add Drone", use_container_width=True, type="primary")
        
        if submit_drone:
            if not drone_model or not drone_capabilities or not drone_location:
                st.error("❌ Please fill all required fields marked with *")
            else:
                try:
                    with st.spinner("Adding drone to fleet..."):
                        drone_data = {
                            'model': drone_model,
                            'capabilities': drone_capabilities,
                            'status': drone_status,
                            'location': drone_location,
                            'payload_capacity_kg': str(drone_payload),
                            'battery_status': f"{drone_battery}%",
                            'maintenance_due': drone_maintenance_due.strftime('%d-%m-%Y'),
                            'current_assignment': '–'
                        }
                        
                        result = add_new_drone(drone_data)
                        
                        if result.get('success'):
                            st.success(f"✅ Drone added successfully with ID: {result.get('drone_id')}")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"❌ Error adding drone: {str(e)}")
    
    # Show existing drones
    with st.expander("🚁 View Existing Drones"):
        try:
            spreadsheet_id = os.getenv('SPREADSHEET_ID')
            drone_range = os.getenv('DRONE_RANGE')
            drones_df = get_sheet_as_df(spreadsheet_id, drone_range)
            st.dataframe(drones_df, use_container_width=True, height=300)
            st.info(f"Total Drones: {len(drones_df)}")
        except Exception as e:
            st.error(f"Unable to load existing drones: {str(e)}")

# --- ADD MISSION ---
with tab3:
    st.subheader("Add New Mission/Project")
    
    with st.form("add_mission_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            mission_client = st.text_input("Client *", placeholder="e.g., Client E")
            mission_location = st.text_input("Location *", placeholder="e.g., Chennai", key="mission_location")
            mission_skills = st.text_input("Required Skills *", placeholder="e.g., Mapping, Inspection")
            mission_certs = st.text_input("Required Certifications *", placeholder="e.g., DGCA")
        
        with col2:
            mission_start = st.date_input("Start Date *")
            mission_end = st.date_input("End Date *")
            mission_priority = st.selectbox("Priority", ["Standard", "High", "Urgent"])
        
        submit_mission = st.form_submit_button("➕ Add Mission", use_container_width=True, type="primary")
        
        if submit_mission:
            if not mission_client or not mission_location or not mission_skills or not mission_certs:
                st.error("❌ Please fill all required fields marked with *")
            elif mission_end < mission_start:
                st.error("❌ End date must be after start date")
            else:
                try:
                    with st.spinner("Adding mission..."):
                        mission_data = {
                            'client': mission_client,
                            'location': mission_location,
                            'required_skills': mission_skills,
                            'required_certs': mission_certs,
                            'start_date': mission_start.strftime('%d-%m-%Y'),
                            'end_date': mission_end.strftime('%d-%m-%Y'),
                            'priority': mission_priority
                        }
                        
                        result = add_new_mission(mission_data)
                        
                        if result.get('success'):
                            st.success(f"✅ Mission added successfully with ID: {result.get('project_id')}")
                            st.balloons()
                        else:
                            st.error(f"❌ Error: {result.get('message')}")
                except Exception as e:
                    st.error(f"❌ Error adding mission: {str(e)}")
    
    # Show existing missions
    with st.expander("📦 View Existing Missions"):
        try:
            spreadsheet_id = os.getenv('SPREADSHEET_ID')
            mission_range = os.getenv('MISSION_RANGE')
            missions_df = get_sheet_as_df(spreadsheet_id, mission_range)
            st.dataframe(missions_df, use_container_width=True, height=300)
            st.info(f"Total Missions: {len(missions_df)}")
        except Exception as e:
            st.error(f"Unable to load existing missions: {str(e)}")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    💡 Tip: IDs are auto-generated. New pilots get P00X, drones get D00X, missions get PRJ00X
</div>
""", unsafe_allow_html=True)
