# Part of SkyOps Agent system – see README for architecture

"""
This module uses an LLM to parse user input into structured intent.

IMPORTANT:
- The LLM must NOT make decisions
- Output must be structured JSON
"""

import os
import json
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


def parse_intent(query: str) -> Dict:
    """
    Parse user query into structured intent using LLM.
    
    Args:
        query: Natural language user query
    
    Returns:
        Structured intent dictionary with:
            - action: Intent type (query_info, assign_mission, urgent_reassign)
            - entities: Extracted entities (pilot_name, drone_id, mission_id, etc.)
            - parameters: Additional parameters
    """
    
    # For now, use simple keyword-based parsing
    # TODO: Replace with actual LLM API call (OpenAI/Anthropic)
    
    query_lower = query.lower()
    
    # Detect action type
    action = _detect_action(query_lower)
    
    # Extract entities
    entities = _extract_entities(query)
    
    # Extract parameters
    parameters = _extract_parameters(query_lower)
    
    return {
        'action': action,
        'entities': entities,
        'parameters': parameters,
        'original_query': query
    }


def _detect_action(query_lower: str) -> str:
    """
    Detect the intent action from the query.
    """
    # Urgent reassignment keywords
    if any(word in query_lower for word in ['urgent', 'emergency', 'reassign', 'move', 'transfer']):
        if any(word in query_lower for word in ['reassign', 'move', 'transfer', 'switch']):
            return 'urgent_reassign'
    
    # Assignment keywords
    if any(word in query_lower for word in ['assign', 'allocate', 'schedule', 'book', 'give']):
        return 'assign_mission'
    
    # Query keywords (default)
    if any(word in query_lower for word in ['show', 'list', 'who', 'what', 'which', 'status', 'available', 'check', 'find', 'get']):
        return 'query_info'
    
    # Default to query
    return 'query_info'


def _extract_entities(query: str) -> Dict:
    """
    Extract entities from the query (pilot names, drone IDs, mission IDs).
    """
    entities = {}
    
    # Extract pilot names (capitalized words that look like names)
    words = query.split()
    for i, word in enumerate(words):
        if word[0].isupper() and len(word) > 2:
            # Check if it's after "pilot", "assign", or similar context
            if i > 0 and words[i-1].lower() in ['pilot', 'assign', 'schedule']:
                entities['pilot_name'] = word
                break
            # Or if it's a standalone capitalized word (likely a name)
            elif word not in ['Mission', 'Drone', 'Project', 'Client']:
                entities['pilot_name'] = word
    
    # Extract drone IDs (pattern: D followed by digits or specific formats)
    for word in words:
        if word.startswith('D') and any(c.isdigit() for c in word):
            entities['drone_id'] = word
            break
        elif 'drone' in query.lower():
            # Try to find the next word after "drone"
            drone_idx = [i for i, w in enumerate(words) if 'drone' in w.lower()]
            if drone_idx and drone_idx[0] + 1 < len(words):
                entities['drone_id'] = words[drone_idx[0] + 1]
                break
    
    # Extract mission/project IDs (pattern: PRJ or Project followed by identifier)
    for word in words:
        if word.startswith('PRJ') or word.startswith('Project'):
            entities['mission_id'] = word
            break
        elif word.startswith('Mission'):
            entities['mission_id'] = word
            break
    
    # Extract "from" and "to" missions for reassignment
    if 'from' in query.lower() and 'to' in query.lower():
        from_idx = [i for i, w in enumerate(words) if w.lower() == 'from']
        to_idx = [i for i, w in enumerate(words) if w.lower() == 'to']
        
        if from_idx and to_idx:
            # Get mission after "from"
            if from_idx[0] + 1 < len(words):
                entities['from_mission_id'] = words[from_idx[0] + 1]
            # Get mission after "to"
            if to_idx[0] + 1 < len(words):
                entities['to_mission_id'] = words[to_idx[0] + 1]
    
    return entities


def _extract_parameters(query_lower: str) -> Dict:
    """
    Extract additional parameters from the query.
    """
    parameters = {}
    
    # Determine query type
    if 'pilot' in query_lower:
        parameters['query_type'] = 'pilots'
    elif 'drone' in query_lower:
        parameters['query_type'] = 'drones'
    elif 'mission' in query_lower or 'project' in query_lower:
        parameters['query_type'] = 'missions'
    else:
        parameters['query_type'] = 'summary'
    
    # Check for urgent flag
    if any(word in query_lower for word in ['urgent', 'emergency', 'asap', 'immediately']):
        parameters['urgent'] = True
    else:
        parameters['urgent'] = False
    
    return parameters


def parse_intent_with_llm(query: str, api_provider: str = 'openai') -> Dict:
    """
    Parse intent using actual LLM API (OpenAI or Anthropic).
    
    Args:
        query: User query
        api_provider: 'openai' or 'anthropic'
    
    Returns:
        Structured intent dictionary
    """
    
    system_prompt = """You are an intent parser for a drone operations system.
Your ONLY job is to extract structured information from user queries.
You must NOT make operational decisions.

Parse the query and return JSON with:
{
    "action": "query_info" | "assign_mission" | "urgent_reassign",
    "entities": {
        "pilot_name": "...",
        "drone_id": "...",
        "mission_id": "...",
        "from_mission_id": "...",
        "to_mission_id": "..."
    },
    "parameters": {
        "query_type": "pilots" | "drones" | "missions" | "summary",
        "urgent": true | false
    }
}

Examples:
- "Show me available pilots" -> {"action": "query_info", "entities": {}, "parameters": {"query_type": "pilots"}}
- "Assign Arjun to Mission Alpha with Drone D001" -> {"action": "assign_mission", "entities": {"pilot_name": "Arjun", "mission_id": "Alpha", "drone_id": "D001"}, "parameters": {}}
- "Urgent: Move Drone D001 from Project A to Project B" -> {"action": "urgent_reassign", "entities": {"drone_id": "D001", "from_mission_id": "A", "to_mission_id": "B"}, "parameters": {"urgent": true}}

Return ONLY valid JSON, no explanations."""

    if api_provider == 'openai':
        return _parse_with_openai(query, system_prompt)
    elif api_provider == 'anthropic':
        return _parse_with_anthropic(query, system_prompt)
    else:
        # Fallback to simple parsing
        return parse_intent(query)


def _parse_with_openai(query: str, system_prompt: str) -> Dict:
    """
    Parse intent using OpenAI API.
    """
    try:
        import openai
        
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print("Warning: OPENAI_API_KEY not set, using simple parser")
            return parse_intent(query)
        
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            temperature=0,
            response_format={"type": "json_object"}
        )
        
        intent = json.loads(response.choices[0].message.content)
        intent['original_query'] = query
        return intent
        
    except Exception as e:
        print(f"Error using OpenAI API: {e}. Falling back to simple parser.")
        return parse_intent(query)


def _parse_with_anthropic(query: str, system_prompt: str) -> Dict:
    """
    Parse intent using Anthropic API.
    """
    try:
        import anthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not set, using simple parser")
            return parse_intent(query)
        
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            system=system_prompt,
            messages=[
                {"role": "user", "content": query}
            ]
        )
        
        intent = json.loads(message.content[0].text)
        intent['original_query'] = query
        return intent
        
    except Exception as e:
        print(f"Error using Anthropic API: {e}. Falling back to simple parser.")
        return parse_intent(query)

