# Part of SkyOps Agent system – see README for architecture

"""
Data View page - Statistics and Analytics Dashboard
"""

import streamlit as st
import pandas as pd
from tools.sheets import get_sheet_as_df
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Analytics - SkyOps Agent",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better visuals
st.markdown("""
    <style>
    .stat-card {
        padding: 1.5rem;
        border-radius: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .stat-card-green {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .stat-card-orange {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .stat-card-blue {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .big-number {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
    }
    .stat-label {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div style="text-align: center;"><h1>📊 Operations Analytics</h1></div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">Real-time insights into drone operations</div>', unsafe_allow_html=True)

# Add refresh button
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

st.divider()

# Load data with caching
@st.cache_data(ttl=60)
def load_all_data():
    """Load all data from Google Sheets with caching."""
    try:
        spreadsheet_id = os.getenv('SPREADSHEET_ID')
        pilot_range = os.getenv('PILOT_RANGE')
        drone_range = os.getenv('DRONE_RANGE')
        mission_range = os.getenv('MISSION_RANGE')
        
        pilots_df = get_sheet_as_df(spreadsheet_id, pilot_range)
        drones_df = get_sheet_as_df(spreadsheet_id, drone_range)
        missions_df = get_sheet_as_df(spreadsheet_id, mission_range)
        return pilots_df, drones_df, missions_df, None
    except Exception as e:
        return None, None, None, str(e)

# Load data
with st.spinner("Loading operational data..."):
    pilots_df, drones_df, missions_df, error = load_all_data()

if error:
    st.error(f"❌ Error loading data: {error}")
    st.stop()

# === KEY METRICS ===
st.markdown("### 📈 Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

with col1:
    total_pilots = len(pilots_df)
    available_pilots = len(pilots_df[pilots_df['status'].str.lower() == 'available'])
    st.markdown(f"""
    <div class="stat-card">
        <div class="big-number">{total_pilots}</div>
        <div class="stat-label">Total Pilots</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="stat-card stat-card-green">
        <div class="big-number">{available_pilots}</div>
        <div class="stat-label">Available Pilots</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    total_drones = len(drones_df)
    available_drones = len(drones_df[drones_df['status'].str.lower() == 'available'])
    st.markdown(f"""
    <div class="stat-card">
        <div class="big-number">{total_drones}</div>
        <div class="stat-label">Total Drones</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="stat-card stat-card-orange">
        <div class="big-number">{available_drones}</div>
        <div class="stat-label">Available Drones</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# === RESOURCE UTILIZATION ===
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 👨‍✈️ Pilot Status Distribution")
    
    if 'status' in pilots_df.columns:
        status_counts = pilots_df['status'].value_counts()
        
        # Create bar chart data
        chart_data = pd.DataFrame({
            'Status': status_counts.index,
            'Count': status_counts.values
        })
        
        st.bar_chart(chart_data.set_index('Status'))
        
        # Show percentages
        st.markdown("**Breakdown:**")
        for status, count in status_counts.items():
            percentage = (count / len(pilots_df)) * 100
            if status.lower() == 'available':
                st.success(f"✅ {status}: {count} ({percentage:.1f}%)")
            elif status.lower() == 'assigned':
                st.info(f"📌 {status}: {count} ({percentage:.1f}%)")
            else:
                st.warning(f"⚠️ {status}: {count} ({percentage:.1f}%)")

with col2:
    st.markdown("### 🚁 Drone Status Distribution")
    
    if 'status' in drones_df.columns:
        drone_status_counts = drones_df['status'].value_counts()
        
        # Create bar chart data
        chart_data_drone = pd.DataFrame({
            'Status': drone_status_counts.index,
            'Count': drone_status_counts.values
        })
        
        st.bar_chart(chart_data_drone.set_index('Status'))
        
        # Show percentages
        st.markdown("**Breakdown:**")
        for status, count in drone_status_counts.items():
            percentage = (count / len(drones_df)) * 100
            if status.lower() == 'available':
                st.success(f"✅ {status}: {count} ({percentage:.1f}%)")
            elif status.lower() == 'assigned':
                st.info(f"📌 {status}: {count} ({percentage:.1f}%)")
            else:
                st.error(f"🔧 {status}: {count} ({percentage:.1f}%)")

st.divider()

# === LOCATION DISTRIBUTION ===
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 📍 Pilots by Location")
    
    if 'location' in pilots_df.columns:
        location_counts = pilots_df['location'].value_counts()
        
        for location, count in location_counts.items():
            percentage = (count / len(pilots_df)) * 100
            st.metric(location, f"{count} pilots", f"{percentage:.0f}% of total")

with col2:
    st.markdown("### 📍 Drones by Location")
    
    if 'location' in drones_df.columns:
        drone_location_counts = drones_df['location'].value_counts()
        
        for location, count in drone_location_counts.items():
            percentage = (count / len(drones_df)) * 100
            st.metric(location, f"{count} drones", f"{percentage:.0f}% of total")

st.divider()

# === MISSION ANALYTICS ===
st.markdown("### 📦 Mission Analytics")

col1, col2, col3 = st.columns(3)

with col1:
    total_missions = len(missions_df)
    st.markdown(f"""
    <div class="stat-card stat-card-blue">
        <div class="big-number">{total_missions}</div>
        <div class="stat-label">Active Missions</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Calculate fully assigned missions
    assigned_missions = 0
    for _, mission in missions_df.iterrows():
        mission_id = mission.get('project_id', '')
        has_pilot = any(pilots_df.get('current_assignment', '') == mission_id)
        has_drone = any(drones_df.get('current_assignment', '') == mission_id)
        if has_pilot and has_drone:
            assigned_missions += 1
    
    assignment_rate = (assigned_missions / total_missions * 100) if total_missions > 0 else 0
    st.markdown(f"""
    <div class="stat-card stat-card-green">
        <div class="big-number">{assignment_rate:.0f}%</div>
        <div class="stat-label">Assignment Rate</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    if 'priority' in missions_df.columns:
        urgent_missions = len(missions_df[missions_df['priority'].str.lower() == 'urgent'])
        st.markdown(f"""
        <div class="stat-card stat-card-orange">
            <div class="big-number">{urgent_missions}</div>
            <div class="stat-label">Urgent Missions</div>
        </div>
        """, unsafe_allow_html=True)

# Mission breakdown
if 'priority' in missions_df.columns:
    st.markdown("#### Mission Priority Distribution")
    priority_counts = missions_df['priority'].value_counts()
    
    col1, col2, col3 = st.columns(3)
    for i, (priority, count) in enumerate(priority_counts.items()):
        percentage = (count / len(missions_df)) * 100
        with [col1, col2, col3][i % 3]:
            if priority.lower() == 'urgent':
                st.error(f"🚨 {priority}: {count} ({percentage:.0f}%)")
            elif priority.lower() == 'high':
                st.warning(f"⚡ {priority}: {count} ({percentage:.0f}%)")
            else:
                st.info(f"📋 {priority}: {count} ({percentage:.0f}%)")

st.divider()

# === ASSIGNMENT MATRIX ===
st.markdown("### 🔗 Assignment Overview")

# Build assignment summary
assignments = []
for _, mission in missions_df.iterrows():
    mission_id = mission.get('project_id', 'N/A')
    
    # Find assigned pilot
    assigned_pilots = pilots_df[pilots_df.get('current_assignment', '') == mission_id]
    pilot_name = assigned_pilots.iloc[0]['name'] if not assigned_pilots.empty else '❌ Unassigned'
    
    # Find assigned drone
    assigned_drones = drones_df[drones_df.get('current_assignment', '') == mission_id]
    drone_id = assigned_drones.iloc[0]['drone_id'] if not assigned_drones.empty else '❌ Unassigned'
    
    assignments.append({
        'Mission': mission_id,
        'Client': mission.get('client', 'N/A'),
        'Location': mission.get('location', 'N/A'),
        'Pilot': pilot_name,
        'Drone': drone_id,
        'Priority': mission.get('priority', 'N/A')
    })

assignments_df = pd.DataFrame(assignments)

# Assignment statistics
col1, col2, col3 = st.columns(3)

with col1:
    fully_assigned = len([a for a in assignments if '❌' not in a['Pilot'] and '❌' not in a['Drone']])
    st.metric("✅ Fully Assigned", f"{fully_assigned}/{total_missions}", 
              delta=f"{(fully_assigned/total_missions*100):.0f}%" if total_missions > 0 else "0%")

with col2:
    partial = len([a for a in assignments if ('❌' in a['Pilot']) != ('❌' in a['Drone'])])
    st.metric("⚠️ Partially Assigned", partial)

with col3:
    unassigned = len([a for a in assignments if '❌' in a['Pilot'] and '❌' in a['Drone']])
    st.metric("❌ Unassigned", unassigned)

# Show assignment table
with st.expander("📋 View Detailed Assignment Matrix"):
    st.dataframe(assignments_df, use_container_width=True, height=300)

st.divider()

# === CAPACITY PLANNING ===
st.markdown("### 📊 Capacity Planning")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### Pilot Capacity")
    pilot_utilization = ((total_pilots - available_pilots) / total_pilots * 100) if total_pilots > 0 else 0
    st.progress(pilot_utilization / 100)
    st.markdown(f"**Utilization:** {pilot_utilization:.0f}% ({total_pilots - available_pilots}/{total_pilots} in use)")
    
    if pilot_utilization > 80:
        st.error("⚠️ High utilization! Consider hiring more pilots.")
    elif pilot_utilization > 50:
        st.warning("📊 Moderate utilization. Monitor capacity.")
    else:
        st.success("✅ Good capacity available.")

with col2:
    st.markdown("#### Drone Capacity")
    drone_utilization = ((total_drones - available_drones) / total_drones * 100) if total_drones > 0 else 0
    st.progress(drone_utilization / 100)
    st.markdown(f"**Utilization:** {drone_utilization:.0f}% ({total_drones - available_drones}/{total_drones} in use)")
    
    if drone_utilization > 80:
        st.error("⚠️ High utilization! Consider acquiring more drones.")
    elif drone_utilization > 50:
        st.warning("📊 Moderate utilization. Monitor capacity.")
    else:
        st.success("✅ Good capacity available.")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    📊 Data refreshes every 60 seconds | Analytics updated in real-time
</div>
""", unsafe_allow_html=True)
