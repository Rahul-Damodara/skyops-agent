# Debug script to test assignment

from intent_parser import parse_intent
from agent.coordinator import run_agent
from tools.sheets import get_sheet_as_df
import os
from dotenv import load_dotenv

load_dotenv()

# Test query
query = "Assign Arjun to PRJ001 with Drone D001"

print("=" * 60)
print("DEBUGGING ASSIGNMENT")
print("=" * 60)

# Step 1: Check what intent parser extracts
print("\n1. Intent Parser Output:")
intent = parse_intent(query)
print(f"   Action: {intent['action']}")
print(f"   Entities: {intent['entities']}")
print(f"   Parameters: {intent['parameters']}")

# Step 2: Check what's in the sheets
print("\n2. Checking Google Sheets Data:")
spreadsheet_id = os.getenv('SPREADSHEET_ID')

pilots_df = get_sheet_as_df(spreadsheet_id, 'pilot_roster!A:Z')
print(f"\n   Pilots in sheet:")
print(f"   {pilots_df[['pilot_id', 'name', 'status']].to_string()}")

drones_df = get_sheet_as_df(spreadsheet_id, 'drone_fleet!A:Z')
print(f"\n   Drones in sheet:")
print(f"   {drones_df[['drone_id', 'model', 'status']].to_string()}")

missions_df = get_sheet_as_df(spreadsheet_id, 'missions!A:Z')
print(f"\n   Missions in sheet:")
print(f"   {missions_df[['project_id', 'client', 'location']].to_string()}")

# Step 3: Test name matching
print("\n3. Testing Name Matching:")
pilot_name_from_intent = intent['entities'].get('pilot_name')
print(f"   Pilot name from intent: '{pilot_name_from_intent}'")

if pilot_name_from_intent:
    pilot_match = pilots_df[
        pilots_df['name'].str.lower() == pilot_name_from_intent.lower()
    ]
    print(f"   Match found: {not pilot_match.empty}")
    if not pilot_match.empty:
        print(f"   Matched pilot: {pilot_match.iloc[0]['name']}")
    else:
        print(f"   All pilot names: {pilots_df['name'].tolist()}")

# Step 4: Test drone matching
print("\n4. Testing Drone Matching:")
drone_id_from_intent = intent['entities'].get('drone_id')
print(f"   Drone ID from intent: '{drone_id_from_intent}'")

if drone_id_from_intent:
    drone_match = drones_df[
        drones_df['drone_id'].str.upper() == drone_id_from_intent.upper()
    ]
    print(f"   Match found: {not drone_match.empty}")
    if not drone_match.empty:
        print(f"   Matched drone: {drone_match.iloc[0]['drone_id']}")
    else:
        print(f"   All drone IDs: {drones_df['drone_id'].tolist()}")

# Step 5: Test mission matching
print("\n5. Testing Mission Matching:")
mission_id_from_intent = intent['entities'].get('mission_id')
print(f"   Mission ID from intent: '{mission_id_from_intent}'")

if mission_id_from_intent:
    mission_match = missions_df[
        missions_df['project_id'].str.upper() == mission_id_from_intent.upper()
    ]
    print(f"   Match found: {not mission_match.empty}")
    if not mission_match.empty:
        print(f"   Matched mission: {mission_match.iloc[0]['project_id']}")
    else:
        print(f"   All mission IDs: {missions_df['project_id'].tolist()}")

print("\n" + "=" * 60)
print("Now running full agent...")
print("=" * 60)

# Run the full agent
result = run_agent(query, use_llm=False)
print(f"\nResult:")
print(f"  Success: {result['success']}")
print(f"  Message: {result['message']}")
