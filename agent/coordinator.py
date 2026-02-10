# Part of SkyOps Agent system – see README for architecture

"""
Main agent loop for SkyOps.

Responsibilities:
- Parse user intent
- Plan execution steps
- Load data from Google Sheets
- Apply rules
- Take action or return explanations
"""

import os
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
import pandas as pd

# Import agent modules
from agent.planner import plan, validate_intent
from agent.rules import validate_assignment, check_mission_feasibility
from agent.memory import agent_state

# Import tools
from tools.sheets import get_sheet_as_df, update_sheet_from_df
from tools.pilots import add_new_pilot
from tools.drones import add_new_drone
from tools.missions import add_new_mission
from intent_parser import parse_intent, parse_intent_with_llm

load_dotenv()


def run_agent(user_query: str, use_llm: bool = False) -> Dict:
    """
    Main agent loop that processes user queries.
    
    Args:
        user_query: Natural language query from user
        use_llm: Whether to use LLM for intent parsing (default: False, uses simple parser)
    
    Returns:
        Dictionary with:
            - success: Boolean indicating if operation succeeded
            - message: Human-readable response
            - data: Any relevant data to display
            - steps_taken: List of steps executed
    """
    
    # Step 1: Parse user intent
    if use_llm:
        intent = parse_intent_with_llm(user_query)
    else:
        intent = parse_intent(user_query)
    
    # Validate intent structure
    is_valid, error_msg = validate_intent(intent)
    if not is_valid:
        return {
            'success': False,
            'message': f"Could not understand request: {error_msg}",
            'data': None,
            'steps_taken': []
        }
    
    # Step 2: Create execution plan
    execution_plan = plan(intent)
    
    # Step 3: Execute the plan
    result = _execute_plan(execution_plan, intent)
    
    # Step 4: Update agent memory
    agent_state['last_decision'] = {
        'query': user_query,
        'intent': intent,
        'result': result
    }
    
    return result


def _execute_plan(execution_plan: List[Dict], intent: Dict) -> Dict:
    """
    Execute the planned steps.
    """
    steps_taken = []
    context = {
        'pilots_df': None,
        'drones_df': None,
        'missions_df': None,
        'resolved_entities': {}
    }
    
    try:
        for step in execution_plan:
            tool = step['tool']
            params = step['params']
            description = step['description']
            
            steps_taken.append(description)
            
            # Execute the tool
            if tool == 'load_pilots':
                context['pilots_df'] = _load_pilots()
            
            elif tool == 'load_drones':
                context['drones_df'] = _load_drones()
            
            elif tool == 'load_missions':
                context['missions_df'] = _load_missions()
            
            elif tool == 'resolve_entities':
                context['resolved_entities'] = _resolve_entities(params, context)
            
            elif tool == 'validate_assignment':
                validation_result = _validate_assignment_step(context)
                if not validation_result['success']:
                    return validation_result
            
            elif tool == 'execute_assignment':
                return _execute_assignment(context, steps_taken)
            
            elif tool == 'validate_reassignment':
                validation_result = _validate_reassignment_step(context, params)
                if not validation_result['success']:
                    return validation_result
            
            elif tool == 'execute_reassignment':
                return _execute_reassignment(context, steps_taken)
            
            elif tool == 'set_urgent_mode':
                agent_state['urgent_mode'] = params.get('urgent', False)
            
            elif tool == 'parse_pilot_info':
                context['new_pilot_data'] = _parse_pilot_info(intent)
            
            elif tool == 'add_pilot':
                return _add_pilot_handler(context, steps_taken, intent)
            
            elif tool == 'parse_drone_info':
                context['new_drone_data'] = _parse_drone_info(intent)
            
            elif tool == 'add_drone':
                return _add_drone_handler(context, steps_taken, intent)
            
            elif tool == 'parse_mission_info':
                context['new_mission_data'] = _parse_mission_info(intent)
            
            elif tool == 'add_mission':
                return _add_mission_handler(context, steps_taken, intent)
            
            elif tool == 'format_query_response':
                return _format_query_response(context, params, steps_taken)
            
            elif tool == 'format_confirmation':
                return _format_confirmation(context, params, steps_taken)
            
            elif tool == 'unknown_intent':
                return {
                    'success': False,
                    'message': step['description'],
                    'data': None,
                    'steps_taken': steps_taken
                }
        
        # If we got here without returning, something went wrong
        return {
            'success': False,
            'message': "Execution completed but no result was generated",
            'data': None,
            'steps_taken': steps_taken
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error during execution: {str(e)}",
            'data': None,
            'steps_taken': steps_taken
        }


def _load_pilots() -> pd.DataFrame:
    """Load pilots from Google Sheets."""
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    pilots_range = os.getenv('PILOTS_SHEET_RANGE')
    return get_sheet_as_df(spreadsheet_id, pilots_range)


def _load_drones() -> pd.DataFrame:
    """Load drones from Google Sheets."""
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    drones_range = os.getenv('DRONES_SHEET_RANGE')
    return get_sheet_as_df(spreadsheet_id, drones_range)


def _load_missions() -> pd.DataFrame:
    """Load missions from Google Sheets."""
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    missions_range = os.getenv('MISSIONS_SHEET_RANGE')
    return get_sheet_as_df(spreadsheet_id, missions_range)


def _resolve_entities(params: Dict, context: Dict) -> Dict:
    """
    Resolve entity names/IDs to actual records.
    """
    resolved = {}
    
    # Resolve pilot
    pilot_name = params.get('pilot_name')
    if pilot_name and context['pilots_df'] is not None:
        pilot_match = context['pilots_df'][
            context['pilots_df']['name'].str.lower() == pilot_name.lower()
        ]
        if not pilot_match.empty:
            resolved['pilot'] = pilot_match.iloc[0].to_dict()
        else:
            resolved['pilot'] = None
    
    # Resolve drone
    drone_id = params.get('drone_id')
    if drone_id and context['drones_df'] is not None:
        drone_match = context['drones_df'][
            context['drones_df']['drone_id'].str.upper() == drone_id.upper()
        ]
        if not drone_match.empty:
            resolved['drone'] = drone_match.iloc[0].to_dict()
        else:
            resolved['drone'] = None
    
    # Resolve mission
    mission_id = params.get('mission_id')
    if mission_id and context['missions_df'] is not None:
        mission_match = context['missions_df'][
            context['missions_df']['project_id'].str.upper() == mission_id.upper()
        ]
        if not mission_match.empty:
            resolved['mission'] = mission_match.iloc[0].to_dict()
        else:
            resolved['mission'] = None
    
    # Resolve from_mission (for reassignment)
    from_mission_id = params.get('from_mission_id')
    if from_mission_id and context['missions_df'] is not None:
        from_mission_match = context['missions_df'][
            context['missions_df']['project_id'].str.upper() == from_mission_id.upper()
        ]
        if not from_mission_match.empty:
            resolved['from_mission'] = from_mission_match.iloc[0].to_dict()
        else:
            resolved['from_mission'] = None
    
    # Resolve to_mission (for reassignment)
    to_mission_id = params.get('to_mission_id')
    if to_mission_id and context['missions_df'] is not None:
        to_mission_match = context['missions_df'][
            context['missions_df']['project_id'].str.upper() == to_mission_id.upper()
        ]
        if not to_mission_match.empty:
            resolved['to_mission'] = to_mission_match.iloc[0].to_dict()
        else:
            resolved['to_mission'] = None
    
    return resolved


def _validate_assignment_step(context: Dict) -> Dict:
    """
    Validate the assignment using the rules engine.
    """
    resolved = context['resolved_entities']
    
    # Check if entities were found
    if not resolved.get('pilot'):
        return {
            'success': False,
            'message': "Could not find the specified pilot",
            'data': None,
            'steps_taken': []
        }
    
    if not resolved.get('drone'):
        return {
            'success': False,
            'message': "Could not find the specified drone",
            'data': None,
            'steps_taken': []
        }
    
    if not resolved.get('mission'):
        return {
            'success': False,
            'message': "Could not find the specified mission",
            'data': None,
            'steps_taken': []
        }
    
    # Run validation
    blocking_issues, warnings = validate_assignment(
        resolved['pilot'],
        resolved['drone'],
        resolved['mission'],
        context['pilots_df'].to_dict('records'),
        context['drones_df'].to_dict('records'),
        context['missions_df'].to_dict('records')
    )
    
    # Store validation results
    context['validation'] = {
        'blocking_issues': blocking_issues,
        'warnings': warnings
    }
    
    # If there are blocking issues, return failure
    if blocking_issues:
        issues_text = '\n'.join([f"❌ {issue}" for issue in blocking_issues])
        warnings_text = '\n'.join([f"⚠️  {warning}" for warning in warnings]) if warnings else ""
        
        message = f"Assignment validation failed:\n\n{issues_text}"
        if warnings_text:
            message += f"\n\nWarnings:\n{warnings_text}"
        
        return {
            'success': False,
            'message': message,
            'data': {
                'blocking_issues': blocking_issues,
                'warnings': warnings
            },
            'steps_taken': []
        }
    
    # Validation passed
    return {'success': True}


def _execute_assignment(context: Dict, steps_taken: List[str]) -> Dict:
    """
    Execute the assignment by updating Google Sheets.
    """
    resolved = context['resolved_entities']
    validation = context.get('validation', {})
    
    pilot = resolved['pilot']
    drone = resolved['drone']
    mission = resolved['mission']
    
    # Update pilot status
    pilots_df = context['pilots_df']
    pilot_idx = pilots_df[pilots_df['pilot_id'] == pilot['pilot_id']].index[0]
    pilots_df.at[pilot_idx, 'status'] = 'Assigned'
    pilots_df.at[pilot_idx, 'current_assignment'] = mission['project_id']
    
    # Update drone status
    drones_df = context['drones_df']
    drone_idx = drones_df[drones_df['drone_id'] == drone['drone_id']].index[0]
    drones_df.at[drone_idx, 'status'] = 'Assigned'
    drones_df.at[drone_idx, 'current_assignment'] = mission['project_id']
    
    # Write back to Google Sheets
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    update_sheet_from_df(spreadsheet_id, os.getenv('PILOTS_SHEET_RANGE'), pilots_df)
    update_sheet_from_df(spreadsheet_id, os.getenv('DRONES_SHEET_RANGE'), drones_df)
    
    # Build success message
    warnings = validation.get('warnings', [])
    warnings_text = ""
    if warnings:
        warnings_text = "\n\n⚠️  Warnings:\n" + '\n'.join([f"  • {w}" for w in warnings])
    
    message = f"""✅ Assignment successful!

Pilot: {pilot['name']} ({pilot['pilot_id']})
Drone: {drone['drone_id']} ({drone['model']})
Mission: {mission['project_id']} - {mission['client']}
Location: {mission['location']}
Duration: {mission['start_date']} to {mission['end_date']}{warnings_text}"""
    
    return {
        'success': True,
        'message': message,
        'data': {
            'pilot': pilot,
            'drone': drone,
            'mission': mission,
            'warnings': warnings
        },
        'steps_taken': steps_taken
    }


def _validate_reassignment_step(context: Dict, params: Dict) -> Dict:
    """
    Validate reassignment operation.
    """
    resolved = context['resolved_entities']
    
    # Get the resource being reassigned (pilot or drone)
    pilot = resolved.get('pilot')
    drone = resolved.get('drone')
    from_mission = resolved.get('from_mission')
    to_mission = resolved.get('to_mission')
    
    # Check if entities were found
    if not from_mission:
        return {
            'success': False,
            'message': "Could not find the source mission",
            'data': None,
            'steps_taken': []
        }
    
    if not to_mission:
        return {
            'success': False,
            'message': "Could not find the target mission",
            'data': None,
            'steps_taken': []
        }
    
    # At least one resource must be specified
    if not pilot and not drone:
        return {
            'success': False,
            'message': "Must specify either a pilot or drone to reassign",
            'data': None,
            'steps_taken': []
        }
    
    # If reassigning to new mission, validate against new mission requirements
    warnings = []
    blocking_issues = []
    
    if pilot and to_mission:
        # Check if pilot has required skills for new mission
        required_skills = set(to_mission.get('required_skills', '').split(','))
        required_skills = {s.strip() for s in required_skills if s.strip()}
        
        pilot_skills = set(pilot.get('skills', '').split(','))
        pilot_skills = {s.strip() for s in pilot_skills if s.strip()}
        
        missing_skills = required_skills - pilot_skills
        if missing_skills:
            blocking_issues.append(
                f"Pilot {pilot.get('name')} lacks required skills for new mission: {', '.join(missing_skills)}"
            )
        
        # Check certifications
        required_certs = set(to_mission.get('required_certs', '').split(','))
        required_certs = {c.strip() for c in required_certs if c.strip()}
        
        pilot_certs = set(pilot.get('certifications', '').split(','))
        pilot_certs = {c.strip() for c in pilot_certs if c.strip()}
        
        missing_certs = required_certs - pilot_certs
        if missing_certs:
            blocking_issues.append(
                f"Pilot {pilot.get('name')} lacks required certifications: {', '.join(missing_certs)}"
            )
        
        # Location warning
        if pilot.get('location') != to_mission.get('location'):
            warnings.append(
                f"Location mismatch: Pilot in {pilot.get('location')}, mission in {to_mission.get('location')}"
            )
    
    if drone and to_mission:
        # Check drone status
        if drone.get('status', '').lower() == 'maintenance':
            blocking_issues.append(f"Drone {drone.get('drone_id')} is in maintenance")
        
        # Location warning
        if drone.get('location') != to_mission.get('location'):
            warnings.append(
                f"Location mismatch: Drone in {drone.get('location')}, mission in {to_mission.get('location')}"
            )
    
    # Store validation results
    context['validation'] = {
        'blocking_issues': blocking_issues,
        'warnings': warnings
    }
    
    # If urgent mode, only hard blocks prevent reassignment
    if params.get('urgent') and blocking_issues:
        issues_text = '\n'.join([f"❌ {issue}" for issue in blocking_issues])
        return {
            'success': False,
            'message': f"Cannot complete urgent reassignment:\n\n{issues_text}",
            'data': {'blocking_issues': blocking_issues, 'warnings': warnings},
            'steps_taken': []
        }
    elif not params.get('urgent') and blocking_issues:
        issues_text = '\n'.join([f"❌ {issue}" for issue in blocking_issues])
        return {
            'success': False,
            'message': f"Reassignment validation failed:\n\n{issues_text}",
            'data': {'blocking_issues': blocking_issues, 'warnings': warnings},
            'steps_taken': []
        }
    
    return {'success': True}


def _execute_reassignment(context: Dict, steps_taken: List[str]) -> Dict:
    """
    Execute resource reassignment.
    """
    resolved = context['resolved_entities']
    validation = context.get('validation', {})
    
    pilot = resolved.get('pilot')
    drone = resolved.get('drone')
    from_mission = resolved.get('from_mission')
    to_mission = resolved.get('to_mission')
    
    pilots_df = context.get('pilots_df')
    drones_df = context.get('drones_df')
    
    # Track what was reassigned
    reassigned_resources = []
    
    # Reassign pilot
    if pilot and pilots_df is not None:
        pilot_idx = pilots_df[pilots_df['pilot_id'] == pilot['pilot_id']].index[0]
        old_assignment = pilots_df.at[pilot_idx, 'current_assignment']
        pilots_df.at[pilot_idx, 'current_assignment'] = to_mission['project_id']
        pilots_df.at[pilot_idx, 'status'] = 'Assigned'
        reassigned_resources.append(f"Pilot {pilot['name']} from {from_mission['project_id']} to {to_mission['project_id']}")
    
    # Reassign drone
    if drone and drones_df is not None:
        drone_idx = drones_df[drones_df['drone_id'] == drone['drone_id']].index[0]
        old_assignment = drones_df.at[drone_idx, 'current_assignment']
        drones_df.at[drone_idx, 'current_assignment'] = to_mission['project_id']
        drones_df.at[drone_idx, 'status'] = 'Assigned'
        reassigned_resources.append(f"Drone {drone['drone_id']} from {from_mission['project_id']} to {to_mission['project_id']}")
    
    # Write back to Google Sheets
    spreadsheet_id = os.getenv('SPREADSHEET_ID')
    
    if pilot and pilots_df is not None:
        update_sheet_from_df(spreadsheet_id, os.getenv('PILOTS_SHEET_RANGE'), pilots_df)
    
    if drone and drones_df is not None:
        update_sheet_from_df(spreadsheet_id, os.getenv('DRONES_SHEET_RANGE'), drones_df)
    
    # Build success message
    warnings = validation.get('warnings', [])
    warnings_text = ""
    if warnings:
        warnings_text = "\n\n⚠️  Warnings:\n" + '\n'.join([f"  • {w}" for w in warnings])
    
    reassignment_list = '\n'.join([f"  • {r}" for r in reassigned_resources])
    
    message = f"""🚨 Urgent Reassignment Completed!

Reassigned:
{reassignment_list}

From Mission: {from_mission['project_id']} - {from_mission['client']}
To Mission: {to_mission['project_id']} - {to_mission['client']}
Target Location: {to_mission['location']}
Duration: {to_mission['start_date']} to {to_mission['end_date']}{warnings_text}

⚠️ Note: {from_mission['project_id']} may need new resource assignment."""
    
    return {
        'success': True,
        'message': message,
        'data': {
            'pilot': pilot,
            'drone': drone,
            'from_mission': from_mission,
            'to_mission': to_mission,
            'warnings': warnings
        },
        'steps_taken': steps_taken
    }


def _format_query_response(context: Dict, params: Dict, steps_taken: List[str]) -> Dict:
    """
    Format query results for display.
    """
    query_type = params.get('query_type', 'summary')
    entities = params.get('entities', {})
    
    data = {}
    message_parts = []
    
    if query_type == 'pilots' or query_type == 'summary':
        pilots_df = context['pilots_df']
        if pilots_df is not None and not pilots_df.empty:
            data['pilots'] = pilots_df.to_dict('records')
            available_count = len(pilots_df[pilots_df['status'] == 'Available'])
            message_parts.append(f"📋 **Pilots**: {len(pilots_df)} total, {available_count} available")
    
    if query_type == 'drones' or query_type == 'summary':
        drones_df = context['drones_df']
        if drones_df is not None and not drones_df.empty:
            data['drones'] = drones_df.to_dict('records')
            available_count = len(drones_df[drones_df['status'] == 'Available'])
            message_parts.append(f"🚁 **Drones**: {len(drones_df)} total, {available_count} available")
    
    if query_type == 'missions' or query_type == 'summary':
        missions_df = context['missions_df']
        if missions_df is not None and not missions_df.empty:
            data['missions'] = missions_df.to_dict('records')
            message_parts.append(f"📦 **Missions**: {len(missions_df)} active")
    
    message = '\n'.join(message_parts) if message_parts else "No data found"
    
    return {
        'success': True,
        'message': message,
        'data': data,
        'steps_taken': steps_taken
    }


def _format_confirmation(context: Dict, params: Dict, steps_taken: List[str]) -> Dict:
    """
    Format confirmation message.
    """
    action = params.get('action')
    entities = params.get('entities', {})
    
    return {
        'success': True,
        'message': f"Action '{action}' completed successfully",
        'data': entities,
        'steps_taken': steps_taken
    }


def _parse_pilot_info(intent: Dict) -> Dict:
    """
    Parse pilot information from the original query.
    For now, prompts user for complete info via dialog.
    """
    # In a real app, you'd parse from query or show a form
    # For demo, return a structure that the UI can handle
    return {
        'needs_input': True,
        'required_fields': ['name', 'skills', 'certifications', 'location', 'available_from']
    }


def _add_pilot_handler(context: Dict, steps_taken: List[str], intent: Dict) -> Dict:
    """
    Handle adding a new pilot.
    """
    # For command-line style, provide instruction message
    return {
        'success': False,
        'message': '''To add a new pilot, please provide the following information:

**Required:**
- Name
- Skills (comma-separated, e.g., "Mapping, Survey")
- Certifications (comma-separated, e.g., "DGCA, Night Ops")
- Location (e.g., "Bangalore")

**Optional:**
- Available from (date in DD-MM-YYYY format)

**Example command:**
"Add pilot Rajesh with skills Inspection,Thermal, certs DGCA,Night Ops, location Mumbai, available from 15-02-2026"

Or you can directly add to the Google Sheet:
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}''',
        'data': None,
        'steps_taken': steps_taken
    }


def _parse_drone_info(intent: Dict) -> Dict:
    """
    Parse drone information from the original query.
    """
    return {
        'needs_input': True,
        'required_fields': ['model', 'capabilities', 'location', 'maintenance_due']
    }


def _add_drone_handler(context: Dict, steps_taken: List[str], intent: Dict) -> Dict:
    """
    Handle adding a new drone.
    """
    return {
        'success': False,
        'message': '''To add a new drone, please provide the following information:

**Required:**
- Model (e.g., "DJI Phantom 4 Pro")
- Capabilities (comma-separated, e.g., "RGB, Thermal")
- Location (e.g., "Bangalore")

**Optional:**
- Maintenance due (date in DD-MM-YYYY format)

**Example command:**
"Add drone DJI Mavic 3 Pro with capabilities RGB,LiDAR at location Bangalore, maintenance due 01-06-2026"

Or you can directly add to the Google Sheet:
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}''',
        'data': None,
        'steps_taken': steps_taken
    }


def _parse_mission_info(intent: Dict) -> Dict:
    """
    Parse mission information from the original query.
    """
    return {
        'needs_input': True,
        'required_fields': ['client', 'location', 'required_skills', 'required_certs', 'start_date', 'end_date', 'priority']
    }


def _add_mission_handler(context: Dict, steps_taken: List[str], intent: Dict) -> Dict:
    """
    Handle adding a new mission.
    """
    return {
        'success': False,
        'message': '''To add a new mission, please provide the following information:

**Required:**
- Client name
- Location
- Required skills (comma-separated)
- Required certifications (comma-separated)
- Start date (DD-MM-YYYY format)
- End date (DD-MM-YYYY format)

**Optional:**
- Priority (High/Urgent/Standard)

**Example command:**
"Add mission for Client D at Hyderabad, requires Mapping,Survey skills, DGCA cert, from 20-02-2026 to 25-02-2026, priority High"

Or you can directly add to the Google Sheet:
https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}''',
        'data': None,
        'steps_taken': steps_taken
    }

