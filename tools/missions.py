# Part of SkyOps Agent system – see README for architecture

"""
Helper functions for mission management.
"""

import pandas as pd
from typing import Dict
from tools.sheets import get_sheet_as_df, append_to_sheet
import os
from dotenv import load_dotenv

load_dotenv()


def add_new_mission(mission_data: Dict) -> Dict:
    """
    Add a new mission/project.
    
    Args:
        mission_data: Dictionary with mission information:
            - client: Client name (required)
            - location: Mission location (required)
            - required_skills: Comma-separated skills (required)
            - required_certs: Comma-separated certifications (required)
            - start_date: Start date in DD-MM-YYYY format (required)
            - end_date: End date in DD-MM-YYYY format (required)
            - priority: Priority level (default "Standard")
    
    Returns:
        Dictionary with success status and project_id
    """
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    missions_range = os.getenv('MISSIONS_SHEET_RANGE')
    
    # Load existing missions to generate new ID
    missions_df = get_sheet_as_df(spreadsheet_id, missions_range)
    
    # Generate new project ID
    if not missions_df.empty:
        # Extract numbers from existing IDs (PRJ001 -> 1)
        existing_ids = missions_df['project_id'].tolist()
        max_num = max([int(pid.replace('PRJ', '')) for pid in existing_ids if pid.startswith('PRJ')])
        new_id = f"PRJ{str(max_num + 1).zfill(3)}"
    else:
        new_id = "PRJ001"
    
    # Create new mission record
    new_mission = {
        'project_id': new_id,
        'client': mission_data.get('client'),
        'location': mission_data.get('location'),
        'required_skills': mission_data.get('required_skills'),
        'required_certs': mission_data.get('required_certs'),
        'start_date': mission_data.get('start_date'),
        'end_date': mission_data.get('end_date'),
        'priority': mission_data.get('priority', 'Standard')
    }
    
    # Validate required fields
    required_fields = ['client', 'location', 'required_skills', 'required_certs', 'start_date', 'end_date']
    missing_fields = [field for field in required_fields if not new_mission.get(field)]
    
    if missing_fields:
        return {
            'success': False,
            'message': f"Missing required fields: {', '.join(missing_fields)}",
            'project_id': None
        }
    
    # Append to sheet
    new_df = pd.DataFrame([new_mission])
    append_to_sheet(spreadsheet_id, missions_range, new_df)
    
    return {
        'success': True,
        'message': f"Mission {new_id} for {new_mission['client']} added successfully",
        'project_id': new_id,
        'mission': new_mission
    }
