# Part of SkyOps Agent system – see README for architecture

"""
Rules engine for validating assignments in SkyOps Agent.

The rules are deterministic and must override any LLM suggestions.

Blocking rules:
- Pilot unavailable
- Skill or certification mismatch
- Drone in maintenance
- Pilot double-booked

Warning rules:
- Location mismatch
"""

from datetime import datetime
from typing import Dict, List, Tuple, Optional


def validate_assignment(
    pilot: Dict, 
    drone: Dict, 
    mission: Dict,
    all_pilots: List[Dict] = None,
    all_drones: List[Dict] = None,
    all_missions: List[Dict] = None
) -> Tuple[List[str], List[str]]:
    """
    Validate a pilot-drone-mission assignment.
    
    Args:
        pilot: Pilot information dictionary
        drone: Drone information dictionary
        mission: Mission information dictionary
        all_pilots: All pilots (for checking double-booking)
        all_drones: All drones (for checking double-booking)
        all_missions: All missions (for checking conflicts)
    
    Returns:
        Tuple of (blocking_issues, warnings)
        - blocking_issues: List of critical errors that prevent assignment
        - warnings: List of non-critical concerns
    """
    blocking_issues = []
    warnings = []
    
    # BLOCKING RULE 1: Check pilot availability status
    if pilot.get('status', '').lower() != 'available':
        status = pilot.get('status', 'unknown')
        blocking_issues.append(f"Pilot {pilot.get('name')} is not available (status: {status})")
    
    # BLOCKING RULE 2: Check if pilot has required skills
    required_skills = mission.get('required_skills', '').split(',')
    required_skills = [s.strip() for s in required_skills if s.strip()]
    pilot_skills = pilot.get('skills', '').split(',')
    pilot_skills = [s.strip() for s in pilot_skills if s.strip()]
    
    missing_skills = [skill for skill in required_skills if skill not in pilot_skills]
    if missing_skills:
        blocking_issues.append(
            f"Pilot {pilot.get('name')} lacks required skills: {', '.join(missing_skills)}"
        )
    
    # BLOCKING RULE 3: Check if pilot has required certifications
    required_certs = mission.get('required_certs', '').split(',')
    required_certs = [c.strip() for c in required_certs if c.strip()]
    pilot_certs = pilot.get('certifications', '').split(',')
    pilot_certs = [c.strip() for c in pilot_certs if c.strip()]
    
    missing_certs = [cert for cert in required_certs if cert not in pilot_certs]
    if missing_certs:
        blocking_issues.append(
            f"Pilot {pilot.get('name')} lacks required certifications: {', '.join(missing_certs)}"
        )
    
    # BLOCKING RULE 4: Check drone maintenance status
    if drone.get('status', '').lower() == 'maintenance':
        blocking_issues.append(
            f"Drone {drone.get('drone_id')} is currently in maintenance"
        )
    
    # BLOCKING RULE 5: Check if drone is already assigned
    if drone.get('current_assignment') and drone.get('current_assignment') != '–' and drone.get('current_assignment') != '-':
        blocking_issues.append(
            f"Drone {drone.get('drone_id')} is already assigned to {drone.get('current_assignment')}"
        )
    
    # BLOCKING RULE 6: Check if pilot is already assigned (double-booking)
    if pilot.get('current_assignment') and pilot.get('current_assignment') != '–' and pilot.get('current_assignment') != '-':
        blocking_issues.append(
            f"Pilot {pilot.get('name')} is already assigned to {pilot.get('current_assignment')}"
        )
    
    # BLOCKING RULE 7: Check drone maintenance due date against mission dates
    try:
        maintenance_due = drone.get('maintenance_due', '')
        mission_start = mission.get('start_date', '')
        mission_end = mission.get('end_date', '')
        
        if maintenance_due and mission_start and mission_end:
            # Parse dates (assuming DD-MM-YYYY format)
            maint_date = datetime.strptime(maintenance_due, '%d-%m-%Y')
            start_date = datetime.strptime(mission_start, '%d-%m-%Y')
            end_date = datetime.strptime(mission_end, '%d-%m-%Y')
            
            if maint_date < end_date:
                blocking_issues.append(
                    f"Drone {drone.get('drone_id')} has maintenance due on {maintenance_due}, which conflicts with mission ending {mission_end}"
                )
    except (ValueError, AttributeError):
        # If date parsing fails, add a warning but don't block
        warnings.append("Unable to verify maintenance schedule against mission dates")
    
    # WARNING RULE 1: Location mismatch
    pilot_location = pilot.get('location', '').strip()
    drone_location = drone.get('location', '').strip()
    mission_location = mission.get('location', '').strip()
    
    if pilot_location and mission_location and pilot_location.lower() != mission_location.lower():
        warnings.append(
            f"Location mismatch: Pilot is in {pilot_location}, mission is in {mission_location}"
        )
    
    if drone_location and mission_location and drone_location.lower() != mission_location.lower():
        warnings.append(
            f"Location mismatch: Drone is in {drone_location}, mission is in {mission_location}"
        )
    
    # WARNING RULE 2: Pilot availability date
    try:
        available_from = pilot.get('available_from', '')
        mission_start = mission.get('start_date', '')
        
        if available_from and mission_start:
            avail_date = datetime.strptime(available_from, '%d-%m-%Y')
            start_date = datetime.strptime(mission_start, '%d-%m-%Y')
            
            if avail_date > start_date:
                warnings.append(
                    f"Pilot {pilot.get('name')} is only available from {available_from}, but mission starts {mission_start}"
                )
    except (ValueError, AttributeError):
        pass
    
    # Return blocking issues and warnings
    return blocking_issues, warnings


def check_mission_feasibility(mission: Dict, all_pilots: List[Dict], all_drones: List[Dict]) -> Dict:
    """
    Check if a mission can be completed with available resources.
    
    Args:
        mission: Mission information
        all_pilots: List of all pilots
        all_drones: List of all drones
    
    Returns:
        Dictionary with feasibility status and available resources
    """
    available_pilots = [p for p in all_pilots if p.get('status', '').lower() == 'available']
    available_drones = [d for d in all_drones if d.get('status', '').lower() == 'available']
    
    # Filter pilots by required skills and certs
    required_skills = set(mission.get('required_skills', '').split(','))
    required_skills = {s.strip() for s in required_skills if s.strip()}
    
    required_certs = set(mission.get('required_certs', '').split(','))
    required_certs = {c.strip() for c in required_certs if c.strip()}
    
    qualified_pilots = []
    for pilot in available_pilots:
        pilot_skills = set(pilot.get('skills', '').split(','))
        pilot_skills = {s.strip() for s in pilot_skills if s.strip()}
        
        pilot_certs = set(pilot.get('certifications', '').split(','))
        pilot_certs = {c.strip() for c in pilot_certs if c.strip()}
        
        if required_skills.issubset(pilot_skills) and required_certs.issubset(pilot_certs):
            qualified_pilots.append(pilot)
    
    return {
        'feasible': len(qualified_pilots) > 0 and len(available_drones) > 0,
        'qualified_pilots': qualified_pilots,
        'available_drones': available_drones,
        'qualified_pilot_count': len(qualified_pilots),
        'available_drone_count': len(available_drones)
    }
