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
    # Similar to validate_assignment but for reassignment
    # For now, return success (implement full logic later)
    return {'success': True}


def _execute_reassignment(context: Dict, steps_taken: List[str]) -> Dict:
    """
    Execute resource reassignment.
    """
    # Implement reassignment logic here
    return {
        'success': True,
        'message': "Reassignment feature coming soon",
        'data': None,
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

