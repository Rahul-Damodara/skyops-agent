# Test Google Sheets connection

from tools.sheets import get_sheet_as_df
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

spreadsheet_id = os.getenv('SPREADSHEET_ID')

# Test reading each sheet
print("Testing Google Sheets connection...\n")

try:
    print("📋 Reading pilot_roster...")
    pilots_df = get_sheet_as_df(spreadsheet_id, 'pilot_roster!A:Z')
    print(f"✅ Found {len(pilots_df)} pilots")
    print(pilots_df.head())
    print()
    
    print("🚁 Reading drone_fleet...")
    drones_df = get_sheet_as_df(spreadsheet_id, 'drone_fleet!A:Z')
    print(f"✅ Found {len(drones_df)} drones")
    print(drones_df.head())
    print()
    
    print("📦 Reading missions...")
    missions_df = get_sheet_as_df(spreadsheet_id, 'missions!A:Z')
    print(f"✅ Found {len(missions_df)} missions")
    print(missions_df.head())
    print()
    
    print("🎉 All sheets connected successfully!")
    
except FileNotFoundError as e:
    print(f"❌ Error: {e}")
    print("Make sure credentials.json is in the project root folder")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check that SPREADSHEET_ID in .env is correct")
    print("2. Verify the service account email has access to the sheet")
    print("3. Ensure sheet tab names match: pilot_roster, drone_fleet, missions")
