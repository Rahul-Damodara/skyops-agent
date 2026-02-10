# Part of SkyOps Agent system – see README for architecture

"""
Agent memory for maintaining conversational and operational state.

This module stores:
- Active mission context
- Urgency flags
- Last decision taken by the agent

This is a lightweight in-memory state.
"""

agent_state = {
    "active_mission": None,
    "urgent_mode": False,
    "last_decision": None
}
