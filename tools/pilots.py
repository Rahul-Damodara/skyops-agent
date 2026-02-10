# Part of SkyOps Agent system – see README for architecture

"""
Helper functions for pilot management.
"""

import pandas as pd
from typing import Dict
from tools.sheets import get_sheet_as_df, append_to_sheet
import os
from dotenv import load_dotenv

load_dotenv()


def add_new_pilot(pilot_data: Dict) -> Dict:
    """
    Add a new pilot to the roster.
    
    Args:
        pilot_data: Dictionary with pilot information:
            - name: Pilot name (required)
            - skills: Comma-separated skills (required)
            - certifications: Comma-separated certifications (required)
            - location: Base location (required)
            - status: Default "Available"
            - current_assignment: Default "–"
            - available_from: Date in DD-MM-YYYY format
    
    Returns:
        Dictionary with success status and pilot_id
    """
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    pilots_range = os.getenv('PILOTS_SHEET_RANGE')
    
    # Load existing pilots to generate new ID
    pilots_df = get_sheet_as_df(spreadsheet_id, pilots_range)
    
    # Generate new pilot ID
    if not pilots_df.empty:
        # Extract numbers from existing IDs (P001 -> 1)
        existing_ids = pilots_df['pilot_id'].tolist()
        max_num = max([int(pid.replace('P', '')) for pid in existing_ids if pid.startswith('P')])
        new_id = f"P{str(max_num + 1).zfill(3)}"
    else:
        new_id = "P001"
    
    # Create new pilot record
    new_pilot = {
        'pilot_id': new_id,
        'name': pilot_data.get('name'),
        'skills': pilot_data.get('skills'),
        'certifications': pilot_data.get('certifications'),
        'location': pilot_data.get('location'),
        'status': pilot_data.get('status', 'Available'),
        'current_assignment': pilot_data.get('current_assignment', '–'),
        'available_from': pilot_data.get('available_from', '')
    }
    
    # Validate required fields
    required_fields = ['name', 'skills', 'certifications', 'location']
    missing_fields = [field for field in required_fields if not new_pilot.get(field)]
    
    if missing_fields:
        return {
            'success': False,
            'message': f"Missing required fields: {', '.join(missing_fields)}",
            'pilot_id': None
        }
    
    # Append to sheet
    new_df = pd.DataFrame([new_pilot])
    append_to_sheet(spreadsheet_id, pilots_range, new_df)
    
    return {
        'success': True,
        'message': f"Pilot {new_pilot['name']} added successfully with ID {new_id}",
        'pilot_id': new_id,
        'pilot': new_pilot
    }
