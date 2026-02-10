# Part of SkyOps Agent system – see README for architecture

"""
Helper functions for drone management.
"""

import pandas as pd
from typing import Dict
from tools.sheets import get_sheet_as_df, append_to_sheet
import os
from dotenv import load_dotenv

load_dotenv()


def add_new_drone(drone_data: Dict) -> Dict:
    """
    Add a new drone to the fleet.
    
    Args:
        drone_data: Dictionary with drone information:
            - model: Drone model (required)
            - capabilities: Comma-separated capabilities (required)
            - location: Current location (required)
            - status: Default "Available"
            - current_assignment: Default "–"
            - maintenance_due: Date in DD-MM-YYYY format
    
    Returns:
        Dictionary with success status and drone_id
    """
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    drones_range = os.getenv('DRONES_SHEET_RANGE')
    
    # Load existing drones to generate new ID
    drones_df = get_sheet_as_df(spreadsheet_id, drones_range)
    
    # Generate new drone ID
    if not drones_df.empty:
        # Extract numbers from existing IDs (D001 -> 1)
        existing_ids = drones_df['drone_id'].tolist()
        max_num = max([int(did.replace('D', '')) for did in existing_ids if did.startswith('D')])
        new_id = f"D{str(max_num + 1).zfill(3)}"
    else:
        new_id = "D001"
    
    # Create new drone record
    new_drone = {
        'drone_id': new_id,
        'model': drone_data.get('model'),
        'capabilities': drone_data.get('capabilities'),
        'status': drone_data.get('status', 'Available'),
        'location': drone_data.get('location'),
        'current_assignment': drone_data.get('current_assignment', '–'),
        'maintenance_due': drone_data.get('maintenance_due', '')
    }
    
    # Validate required fields
    required_fields = ['model', 'capabilities', 'location']
    missing_fields = [field for field in required_fields if not new_drone.get(field)]
    
    if missing_fields:
        return {
            'success': False,
            'message': f"Missing required fields: {', '.join(missing_fields)}",
            'drone_id': None
        }
    
    # Append to sheet
    new_df = pd.DataFrame([new_drone])
    append_to_sheet(spreadsheet_id, drones_range, new_df)
    
    return {
        'success': True,
        'message': f"Drone {new_id} ({new_drone['model']}) added successfully",
        'drone_id': new_id,
        'drone': new_drone
    }
