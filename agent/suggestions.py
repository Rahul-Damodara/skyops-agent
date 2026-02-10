# Part of SkyOps Agent system – see README for architecture

"""
Suggestion engine for finding alternative pilots/drones when assignment fails.
"""

from typing import Dict, List, Tuple
import pandas as pd


def suggest_alternative_pilots(
    mission: Dict,
    all_pilots: List[Dict],
    current_pilot: Dict = None,
    top_n: int = 3
) -> List[Dict]:
    """
    Suggest alternative pilots for a mission based on availability and requirements.
    
    Args:
        mission: Mission information dictionary
        all_pilots: List of all pilot records
        current_pilot: The pilot that was attempted (to exclude from suggestions)
        top_n: Number of top suggestions to return
    
    Returns:
        List of suggested pilots with match scores
    """
    suggestions = []
    
    required_skills = mission.get('required_skills', '').split(',')
    required_skills = [s.strip() for s in required_skills if s.strip()]
    
    required_certs = mission.get('required_certs', '').split(',')
    required_certs = [c.strip() for c in required_certs if c.strip()]
    
    mission_location = mission.get('location', '').strip()
    
    for pilot in all_pilots:
        # Skip the current pilot if provided
        if current_pilot and pilot.get('pilot_id') == current_pilot.get('pilot_id'):
            continue
        
        # Only consider available pilots without assignments
        if pilot.get('status', '').lower() != 'available':
            continue
        
        current_assignment = pilot.get('current_assignment', '')
        if current_assignment and current_assignment not in ['–', '-', 'None', '', 'none']:
            continue
        
        # Calculate match score
        score = 0
        match_details = []
        missing_items = []
        
        # Check skills
        pilot_skills = pilot.get('skills', '').split(',')
        pilot_skills = [s.strip() for s in pilot_skills if s.strip()]
        
        matched_skills = [skill for skill in required_skills if skill in pilot_skills]
        missing_skills = [skill for skill in required_skills if skill not in pilot_skills]
        
        if required_skills:
            skill_match_rate = len(matched_skills) / len(required_skills)
            score += skill_match_rate * 40  # Skills worth 40 points
            
            if matched_skills:
                match_details.append(f"Has skills: {', '.join(matched_skills)}")
            if missing_skills:
                missing_items.append(f"Missing skills: {', '.join(missing_skills)}")
        
        # Check certifications
        pilot_certs = pilot.get('certifications', '').split(',')
        pilot_certs = [c.strip() for c in pilot_certs if c.strip()]
        
        matched_certs = [cert for cert in required_certs if cert in pilot_certs]
        missing_certs = [cert for cert in required_certs if cert not in pilot_certs]
        
        if required_certs:
            cert_match_rate = len(matched_certs) / len(required_certs)
            score += cert_match_rate * 40  # Certifications worth 40 points
            
            if matched_certs:
                match_details.append(f"Has certs: {', '.join(matched_certs)}")
            if missing_certs:
                missing_items.append(f"Missing certs: {', '.join(missing_certs)}")
        
        # Check location
        pilot_location = pilot.get('location', '').strip()
        if pilot_location and mission_location:
            if pilot_location.lower() == mission_location.lower():
                score += 20  # Location match worth 20 points
                match_details.append(f"Same location ({pilot_location})")
            else:
                match_details.append(f"Different location ({pilot_location} vs {mission_location})")
        
        # Only suggest if pilot meets minimum requirements (has all skills and certs)
        if not missing_skills and not missing_certs:
            suggestions.append({
                'pilot': pilot,
                'score': score,
                'match_details': match_details,
                'missing_items': missing_items,
                'qualification': 'Fully Qualified'
            })
        elif score >= 40:  # At least 50% match
            suggestions.append({
                'pilot': pilot,
                'score': score,
                'match_details': match_details,
                'missing_items': missing_items,
                'qualification': 'Partially Qualified'
            })
    
    # Sort by score (descending) and return top N
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return suggestions[:top_n]


def suggest_alternative_drones(
    mission: Dict,
    all_drones: List[Dict],
    current_drone: Dict = None,
    top_n: int = 3
) -> List[Dict]:
    """
    Suggest alternative drones for a mission based on availability.
    
    Args:
        mission: Mission information dictionary
        all_drones: List of all drone records
        current_drone: The drone that was attempted (to exclude from suggestions)
        top_n: Number of top suggestions to return
    
    Returns:
        List of suggested drones with match scores
    """
    suggestions = []
    
    mission_location = mission.get('location', '').strip()
    mission_start = mission.get('start_date', '')
    mission_end = mission.get('end_date', '')
    
    for drone in all_drones:
        # Skip the current drone if provided
        if current_drone and drone.get('drone_id') == current_drone.get('drone_id'):
            continue
        
        # Only consider available drones
        if drone.get('status', '').lower() != 'available':
            continue
        
        # Check if not already assigned
        current_assignment = drone.get('current_assignment', '')
        if current_assignment and current_assignment not in ['–', '-', 'None', '', 'none']:
            continue
        
        # Calculate match score
        score = 50  # Base score for being available
        match_details = ['Status: Available']
        
        # Check location
        drone_location = drone.get('location', '').strip()
        if drone_location and mission_location:
            if drone_location.lower() == mission_location.lower():
                score += 30  # Location match worth 30 points
                match_details.append(f"Same location ({drone_location})")
            else:
                score += 10  # Still available but different location
                match_details.append(f"Different location ({drone_location} vs {mission_location})")
        
        # Check maintenance schedule
        maintenance_due = drone.get('maintenance_due', '')
        if maintenance_due and mission_end:
            from datetime import datetime
            try:
                maint_date = datetime.strptime(maintenance_due, '%d-%m-%Y')
                end_date = datetime.strptime(mission_end, '%d-%m-%Y')
                
                if maint_date > end_date:
                    score += 20  # No maintenance conflict worth 20 points
                    match_details.append('No maintenance conflict')
                else:
                    match_details.append(f'Maintenance due {maintenance_due}')
            except (ValueError, AttributeError):
                pass
        
        suggestions.append({
            'drone': drone,
            'score': score,
            'match_details': match_details,
            'capabilities': drone.get('capabilities', 'N/A')
        })
    
    # Sort by score (descending) and return top N
    suggestions.sort(key=lambda x: x['score'], reverse=True)
    return suggestions[:top_n]


def format_pilot_suggestions(suggestions: List[Dict]) -> str:
    """
    Format pilot suggestions as a readable string.
    
    Args:
        suggestions: List of suggestion dictionaries
    
    Returns:
        Formatted string with suggestions
    """
    if not suggestions:
        return "No alternative pilots available that meet the requirements."
    
    output = "💡 **Suggested Alternative Pilots:**\n\n"
    
    for i, suggestion in enumerate(suggestions, 1):
        pilot = suggestion['pilot']
        score = suggestion['score']
        qualification = suggestion['qualification']
        match_details = suggestion['match_details']
        missing_items = suggestion['missing_items']
        
        output += f"**{i}. {pilot.get('name')} ({pilot.get('pilot_id')})**\n"
        output += f"   - Qualification: {qualification} (Match Score: {score:.0f}/100)\n"
        output += f"   - Location: {pilot.get('location')}\n"
        output += f"   - Skills: {pilot.get('skills')}\n"
        output += f"   - Certifications: {pilot.get('certifications')}\n"
        
        if match_details:
            output += f"   - ✅ {', '.join(match_details)}\n"
        
        if missing_items:
            output += f"   - ⚠️ {', '.join(missing_items)}\n"
        
        output += "\n"
    
    return output


def format_drone_suggestions(suggestions: List[Dict]) -> str:
    """
    Format drone suggestions as a readable string.
    
    Args:
        suggestions: List of suggestion dictionaries
    
    Returns:
        Formatted string with suggestions
    """
    if not suggestions:
        return "No alternative drones available."
    
    output = "💡 **Suggested Alternative Drones:**\n\n"
    
    for i, suggestion in enumerate(suggestions, 1):
        drone = suggestion['drone']
        score = suggestion['score']
        match_details = suggestion['match_details']
        
        output += f"**{i}. {drone.get('drone_id')} ({drone.get('model')})**\n"
        output += f"   - Match Score: {score:.0f}/100\n"
        output += f"   - Location: {drone.get('location')}\n"
        output += f"   - Capabilities: {suggestion.get('capabilities')}\n"
        output += f"   - ✅ {', '.join(match_details)}\n\n"
    
    return output
