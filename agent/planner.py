# Part of SkyOps Agent system – see README for architecture

"""
Planner module for SkyOps Agent.

This module converts high-level intent into a sequence of execution steps.
"""

from typing import Dict, List, Optional


# Supported intents:
# - query_info
# - assign_mission
# - urgent_reassign
# - add_pilot
# - add_drone
# - add_mission


def plan(intent: Dict) -> List[Dict]:
    """
    Convert high-level intent into a sequence of execution steps.
    
    Args:
        intent: Dictionary containing:
            - action: The intent type (query_info, assign_mission, urgent_reassign, add_pilot, add_drone, add_mission)
            - entities: Extracted entities (pilot_name, drone_id, mission_id, etc.)
            - parameters: Additional parameters for the action
    
    Returns:
        List of execution steps, where each step is a dictionary with:
            - tool: The tool to invoke (e.g., 'load_pilots', 'validate_assignment')
            - params: Parameters for the tool
            - description: Human-readable description of the step
    """
    action = intent.get('action', '').lower()
    entities = intent.get('entities', {})
    parameters = intent.get('parameters', {})
    
    if action == 'query_info':
        return _plan_query_info(entities, parameters)
    
    elif action == 'assign_mission':
        return _plan_assign_mission(entities, parameters)
    
    elif action == 'urgent_reassign':
        return _plan_urgent_reassign(entities, parameters)
    
    elif action == 'add_pilot':
        return _plan_add_pilot(entities, parameters)
    
    elif action == 'add_drone':
        return _plan_add_drone(entities, parameters)
    
    elif action == 'add_mission':
        return _plan_add_mission(entities, parameters)
    
    else:
        # Unknown intent - return basic info query
        return [{
            'tool': 'unknown_intent',
            'params': {'intent': intent},
            'description': f"Unknown intent: {action}. Please clarify your request."
        }]


def _plan_query_info(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for querying information about pilots, drones, or missions.
    """
    steps = []
    query_type = parameters.get('query_type', 'summary')
    
    # Step 1: Load relevant data
    if 'pilot_name' in entities or query_type == 'pilots':
        steps.append({
            'tool': 'load_pilots',
            'params': {},
            'description': 'Loading pilot roster from Google Sheets'
        })
    
    if 'drone_id' in entities or query_type == 'drones':
        steps.append({
            'tool': 'load_drones',
            'params': {},
            'description': 'Loading drone fleet from Google Sheets'
        })
    
    if 'mission_id' in entities or query_type == 'missions':
        steps.append({
            'tool': 'load_missions',
            'params': {},
            'description': 'Loading missions from Google Sheets'
        })
    
    # If no specific query, load all data for summary
    if not steps:
        steps.extend([
            {
                'tool': 'load_pilots',
                'params': {},
                'description': 'Loading pilot roster'
            },
            {
                'tool': 'load_drones',
                'params': {},
                'description': 'Loading drone fleet'
            },
            {
                'tool': 'load_missions',
                'params': {},
                'description': 'Loading missions'
            }
        ])
    
    # Step 2: Filter and format the response
    steps.append({
        'tool': 'format_query_response',
        'params': {
            'entities': entities,
            'query_type': query_type
        },
        'description': 'Formatting response for user'
    })
    
    return steps


def _plan_assign_mission(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for assigning a pilot and drone to a mission.
    """
    steps = []
    
    # Step 1: Load all data
    steps.extend([
        {
            'tool': 'load_pilots',
            'params': {},
            'description': 'Loading pilot roster'
        },
        {
            'tool': 'load_drones',
            'params': {},
            'description': 'Loading drone fleet'
        },
        {
            'tool': 'load_missions',
            'params': {},
            'description': 'Loading missions'
        }
    ])
    
    # Step 2: Resolve entities (find the specific pilot, drone, mission)
    steps.append({
        'tool': 'resolve_entities',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'mission_id': entities.get('mission_id')
        },
        'description': f"Resolving pilot '{entities.get('pilot_name')}', drone '{entities.get('drone_id')}', mission '{entities.get('mission_id')}'"
    })
    
    # Step 3: Validate assignment using rules engine
    steps.append({
        'tool': 'validate_assignment',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'mission_id': entities.get('mission_id')
        },
        'description': 'Validating assignment against operational rules'
    })
    
    # Step 4: If validation passes, execute assignment
    steps.append({
        'tool': 'execute_assignment',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'mission_id': entities.get('mission_id')
        },
        'description': 'Executing assignment and updating Google Sheets'
    })
    
    # Step 5: Confirm to user
    steps.append({
        'tool': 'format_confirmation',
        'params': {
            'action': 'assign_mission',
            'entities': entities
        },
        'description': 'Formatting confirmation message'
    })
    
    return steps


def _plan_urgent_reassign(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for urgent reassignment of resources.
    """
    steps = []
    
    # Step 1: Set urgent mode in agent memory
    steps.append({
        'tool': 'set_urgent_mode',
        'params': {'urgent': True},
        'description': 'Activating urgent reassignment mode'
    })
    
    # Step 2: Load all data
    steps.extend([
        {
            'tool': 'load_pilots',
            'params': {},
            'description': 'Loading pilot roster'
        },
        {
            'tool': 'load_drones',
            'params': {},
            'description': 'Loading drone fleet'
        },
        {
            'tool': 'load_missions',
            'params': {},
            'description': 'Loading missions'
        }
    ])
    
    # Step 3: Identify the resource to reassign
    steps.append({
        'tool': 'resolve_entities',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'from_mission_id': entities.get('from_mission_id'),
            'to_mission_id': entities.get('to_mission_id')
        },
        'description': 'Resolving reassignment details'
    })
    
    # Step 4: Validate the urgent reassignment
    steps.append({
        'tool': 'validate_reassignment',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'from_mission_id': entities.get('from_mission_id'),
            'to_mission_id': entities.get('to_mission_id'),
            'urgent': True
        },
        'description': 'Validating urgent reassignment'
    })
    
    # Step 5: Execute reassignment
    steps.append({
        'tool': 'execute_reassignment',
        'params': {
            'pilot_name': entities.get('pilot_name'),
            'drone_id': entities.get('drone_id'),
            'from_mission_id': entities.get('from_mission_id'),
            'to_mission_id': entities.get('to_mission_id')
        },
        'description': 'Executing urgent reassignment and updating records'
    })
    
    # Step 6: Clear urgent mode
    steps.append({
        'tool': 'set_urgent_mode',
        'params': {'urgent': False},
        'description': 'Deactivating urgent mode'
    })
    
    # Step 7: Confirm to user
    steps.append({
        'tool': 'format_confirmation',
        'params': {
            'action': 'urgent_reassign',
            'entities': entities
        },
        'description': 'Formatting urgent reassignment confirmation'
    })
    
    return steps


def _plan_add_pilot(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for adding a new pilot.
    """
    steps = []
    
    # Step 1: Collect pilot information from original query
    steps.append({
        'tool': 'parse_pilot_info',
        'params': {'entities': entities, 'parameters': parameters},
        'description': 'Extracting pilot information from query'
    })
    
    # Step 2: Add pilot to the system
    steps.append({
        'tool': 'add_pilot',
        'params': {'pilot_data': parameters.get('pilot_data', {})},
        'description': 'Adding new pilot to roster'
    })
    
    # Step 3: Confirm addition
    steps.append({
        'tool': 'format_confirmation',
        'params': {'action': 'add_pilot'},
        'description': 'Formatting confirmation message'
    })
    
    return steps


def _plan_add_drone(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for adding a new drone.
    """
    steps = []
    
    # Step 1: Collect drone information from original query
    steps.append({
        'tool': 'parse_drone_info',
        'params': {'entities': entities, 'parameters': parameters},
        'description': 'Extracting drone information from query'
    })
    
    # Step 2: Add drone to the system
    steps.append({
        'tool': 'add_drone',
        'params': {'drone_data': parameters.get('drone_data', {})},
        'description': 'Adding new drone to fleet'
    })
    
    # Step 3: Confirm addition
    steps.append({
        'tool': 'format_confirmation',
        'params': {'action': 'add_drone'},
        'description': 'Formatting confirmation message'
    })
    
    return steps


def _plan_add_mission(entities: Dict, parameters: Dict) -> List[Dict]:
    """
    Plan steps for adding a new mission.
    """
    steps = []
    
    # Step 1: Collect mission information from original query
    steps.append({
        'tool': 'parse_mission_info',
        'params': {'entities': entities, 'parameters': parameters},
        'description': 'Extracting mission information from query'
    })
    
    # Step 2: Add mission to the system
    steps.append({
        'tool': 'add_mission',
        'params': {'mission_data': parameters.get('mission_data', {})},
        'description': 'Adding new mission to schedule'
    })
    
    # Step 3: Confirm addition
    steps.append({
        'tool': 'format_confirmation',
        'params': {'action': 'add_mission'},
        'description': 'Formatting confirmation message'
    })
    
    return steps


def get_supported_intents() -> List[str]:
    """
    Return list of supported intent actions.
    
    Returns:
        List of supported intent action names
    """
    return ['query_info', 'assign_mission', 'urgent_reassign', 'add_pilot', 'add_drone', 'add_mission']


def validate_intent(intent: Dict) -> tuple[bool, Optional[str]]:
    """
    Validate that an intent has the required structure.
    
    Args:
        intent: Intent dictionary to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(intent, dict):
        return False, "Intent must be a dictionary"
    
    if 'action' not in intent:
        return False, "Intent must have an 'action' field"
    
    action = intent.get('action', '').lower()
    if action not in get_supported_intents():
        return False, f"Unsupported action: {action}. Supported: {', '.join(get_supported_intents())}"
    
    if 'entities' not in intent:
        return False, "Intent must have an 'entities' field"
    
    return True, None
