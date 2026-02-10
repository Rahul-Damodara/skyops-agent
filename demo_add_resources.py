# Demo script for adding new resources

from tools.pilots import add_new_pilot
from tools.drones import add_new_drone
from tools.missions import add_new_mission

print("=" * 60)
print("DEMO: Adding New Resources to SkyOps")
print("=" * 60)

# Example 1: Add a new pilot
print("\n1. Adding a new pilot...")
pilot_result = add_new_pilot({
    'name': 'Kavya',
    'skills': 'Mapping, Thermal',
    'certifications': 'DGCA, Night Ops',
    'location': 'Chennai',
    'available_from': '15-02-2026'
})

if pilot_result['success']:
    print(f"   ✅ {pilot_result['message']}")
    print(f"   Pilot ID: {pilot_result['pilot_id']}")
else:
    print(f"   ❌ {pilot_result['message']}")

# Example 2: Add a new drone
print("\n2. Adding a new drone...")
drone_result = add_new_drone({
    'model': 'DJI Phantom 4 Pro',
    'capabilities': 'RGB, Multispectral',
    'location': 'Chennai',
    'maintenance_due': '01-06-2026'
})

if drone_result['success']:
    print(f"   ✅ {drone_result['message']}")
    print(f"   Drone ID: {drone_result['drone_id']}")
else:
    print(f"   ❌ {drone_result['message']}")

# Example 3: Add a new mission
print("\n3. Adding a new mission...")
mission_result = add_new_mission({
    'client': 'Client D',
    'location': 'Hyderabad',
    'required_skills': 'Mapping, Inspection',
    'required_certs': 'DGCA',
    'start_date': '20-02-2026',
    'end_date': '25-02-2026',
    'priority': 'High'
})

if mission_result['success']:
    print(f"   ✅ {mission_result['message']}")
    print(f"   Mission ID: {mission_result['project_id']}")
else:
    print(f"   ❌ {mission_result['message']}")

print("\n" + "=" * 60)
print("Check your Google Sheet to see the new entries!")
print("=" * 60)
