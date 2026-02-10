# SkyOps Agent - System Architecture

**Version:** 1.0  
**Last Updated:** February 10, 2026  
**Project:** Drone Operations Coordinator AI Agent

---

## Architecture Overview

SkyOps Agent is a **deterministic AI agent** built on a hybrid architecture that combines rule-based business logic with optional LLM-powered natural language understanding. The system prioritizes **safety**, **predictability**, and **auditability** over conversational sophistication.

### Core Architectural Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│              (Streamlit Multi-Page Application)              │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Intent Parser Layer                       │
│          (LLM + Keyword Fallback for Resilience)            │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Coordinator (Agent Core)                   │
│         Orchestrates: Planning → Validation → Execution      │
└───────────────────────────┬─────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────────┐
    │ Planner  │    │  Rules   │    │  Suggestions │
    │  Engine  │    │  Engine  │    │    Engine    │
    └──────────┘    └──────────┘    └──────────────┘
           │                │                │
           └────────────────┼────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Tools Layer                             │
│      (Sheets API, Pilots, Drones, Missions Management)      │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Persistence Layer                     │
│                    (Google Sheets API)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Layer-by-Layer Breakdown

### 1. User Interface Layer

**Technology:** Streamlit 1.54.0  
**Location:** `app.py`, `pages/`

#### Components:

**Landing Page** (`app.py`):
- Hero section with gradient branding
- Live statistics dashboard (pilots/drones/missions count)
- Feature showcase cards
- Navigation to sub-pages
- System architecture explanation

**Chat Interface** (`pages/1__Chat.py`):
- Natural language conversation UI
- Message history with chat bubbles
- Quick command shortcuts
- Live data sidebar with resource counts
- Integration with agent coordinator

**Analytics Dashboard** (`pages/2_📊_Analytics.py`):
- Real-time KPI cards
- Status distribution charts (pie/bar)
- Location breakdown
- Mission analytics with priority distribution
- Assignment matrix
- Capacity planning with utilization metrics

**Add Resources** (`pages/3_➕_Add_Resources.py`):
- Form-based interfaces for creating new resources
- Auto-generated IDs (P-XXX, D-XXX, PRJ-XXX)
- Input validation
- Direct Google Sheets integration

---

### 2. Intent Parser Layer

**Location:** `intent_parser.py`  
**Purpose:** Convert natural language to structured intent objects

#### Dual-Mode Architecture:

**Primary Mode: LLM-Powered**
```python
Input: "Assign Arjun to PRJ001 with Drone D001"
↓
LLM Processing (GPT/Claude)
↓
Output: {
    "action": "assign_mission",
    "entities": {
        "pilot_name": "Arjun",
        "mission_id": "PRJ001",
        "drone_id": "D001"
    }
}
```

**Fallback Mode: Keyword-Based**
- Regex patterns for entity extraction
- Action verb matching (assign, remove, query, list)
- Resilient to LLM failures
- Guaranteed system availability

#### Supported Intents:
- `query_pilot` - Get pilot information
- `query_drone` - Get drone details
- `query_mission` - Get mission information
- `list_pilots` - Show all pilots
- `list_drones` - Show all drones
- `list_missions` - Show all missions
- `assign_mission` - Assign pilot+drone to mission
- `remove_assignment` - Unassign resources
- `urgent_reassign` - Emergency reassignment workflow
- `unknown` - Fallback for unrecognized input

---

### 3. Agent Core Layer

#### 3.1 Coordinator (`agent/coordinator.py`)

**Role:** Main orchestration engine  
**Key Functions:**

**`run_agent(user_input, agent_state=None)`**
- Entry point for all agent operations
- Manages agent state across execution
- Routes intents to appropriate handlers
- Returns user-friendly response messages

**Execution Pipeline:**
```
Parse Intent → Generate Plan → Validate → Execute → Sync Data → Return Response
```

**State Management:**
- In-memory state dictionary
- Flags: `urgent_mode`, `last_action`
- Resource caching for performance

**Error Handling:**
- Catch validation failures
- Trigger suggestion engine for alternatives
- Graceful degradation with informative messages

#### 3.2 Planner (`agent/planner.py`)

**Role:** Convert intents into executable action plans  
**Output:** List of step objects with parameters

**Example Plan for Assignment:**
```python
[
    {"step": "load_pilots"},
    {"step": "load_drones"},
    {"step": "load_missions"},
    {"step": "resolve_pilot", "name": "Arjun"},
    {"step": "resolve_drone", "id": "D001"},
    {"step": "resolve_mission", "id": "PRJ001"},
    {"step": "validate_assignment", ...},
    {"step": "execute_assignment", ...},
    {"step": "sync_to_sheets"}
]
```

**Planning Strategies:**
- Query operations: Single-step plans
- Assignments: Multi-step with validation
- Urgent operations: Modified validation rules

#### 3.3 Rules Engine (`agent/rules.py`)

**Role:** Business logic validation  
**Design:** Pure functions for testability

**Validation Categories:**

**Hard Blockers (7 rules):**
```
1. pilot_already_assigned()
2. drone_already_assigned()
3. pilot_missing_skills()
4. pilot_missing_certifications()
5. drone_in_maintenance()
6. mission_date_conflicts()
7. double_booking_check()
```

**Soft Warnings (2 rules):**
```
1. location_mismatch_warning()
2. availability_date_warning()
```

**Return Format:**
```python
{
    "is_valid": False,
    "blocking_issues": ["Pilot P001 already assigned to PRJ005"],
    "warnings": ["Location mismatch: Pilot in Delhi, Mission in Bangalore"]
}
```

#### 3.4 Memory/State (`agent/memory.py`)

**Role:** Temporary state management  
**Implementation:** Python dict with helper functions

**State Schema:**
```python
{
    "urgent_mode": False,
    "last_action": "assign_mission",
    "cached_pilots": [...],
    "cached_drones": [...],
    "cached_missions": [...],
    "timestamp": "2026-02-10T10:30:00"
}
```

#### 3.5 Suggestions Engine (`agent/suggestions.py`)

**Role:** Recommend alternatives when assignments fail  
**Trigger:** Validation failures in coordinator

**Scoring Algorithms:**

**Pilot Scoring:**
```python
score = 0
+ 40% if has all required skills
+ 30% if has all certifications
+ 20% based on location match
+ 10% based on availability date
```

**Drone Scoring:**
```python
score = 0
+ 50% if status is "Available"
+ 30% based on location proximity
+ 20% based on maintenance schedule
```

**Output:** Top 3 alternatives with match scores and justifications

---

### 4. Tools Layer

#### 4.1 Google Sheets Wrapper (`tools/sheets.py`)

**Purpose:** Abstract Google Sheets API complexity  
**Authentication:** Service account with JSON credentials

**Key Functions:**
- `read_sheet(range)` - Read data range
- `update_row(range, values)` - Update specific row
- `append_row(range, values)` - Add new row
- `batch_update()` - Atomic multi-row updates

**Rate Limiting:** Built-in retry logic for API quotas

#### 4.2 Pilots Management (`tools/pilots.py`)

**Functions:**
- `get_all_pilots()` - Load roster from Sheets
- `find_pilot_by_name(name)` - Fuzzy name search
- `find_pilot_by_id(id)` - ID lookup
- `update_pilot_assignment(pilot_id, mission_id)` - Update assignment
- `add_new_pilot(details)` - Create new pilot with auto-ID

**Data Schema:**
```python
{
    "pilot_id": "P001",
    "name": "Arjun Kumar",
    "skills": ["Mapping", "Inspection"],
    "certifications": ["DGCA", "RPTO"],
    "location": "Delhi",
    "status": "Available",
    "assigned_to": "-",
    "available_from": "01-01-2026"
}
```

#### 4.3 Drones Management (`tools/drones.py`)

**Functions:**
- `get_all_drones()` - Load inventory
- `find_drone_by_id(id)` - ID lookup
- `update_drone_assignment(drone_id, mission_id)` - Assign
- `add_new_drone(details)` - Create with auto-ID

**Data Schema:**
```python
{
    "drone_id": "D001",
    "model": "DJI Matrice 300",
    "status": "Available",
    "assigned_to": "-",
    "location": "Mumbai",
    "maintenance_due": "15-06-2026"
}
```

#### 4.4 Missions Management (`tools/missions.py`)

**Functions:**
- `get_all_missions()` - Load all missions
- `find_mission_by_id(id)` - ID lookup
- `add_new_mission(details)` - Create with auto-ID

**Data Schema:**
```python
{
    "mission_id": "PRJ001",
    "name": "Mumbai Port Survey",
    "priority": "High",
    "required_skills": ["Mapping", "Surveying"],
    "required_certifications": ["DGCA"],
    "location": "Mumbai",
    "start_date": "10-02-2026",
    "end_date": "12-02-2026"
}
```

---

### 5. Data Persistence Layer

**Primary Store:** Google Sheets  
**Spreadsheet ID:** `1eyZc_vxlgtVCPthtF8RGCg_JLqNEhRT9gbWwnx7jnY0`

**Sheet Structure:**

| Sheet Name | Range | Columns |
|------------|-------|---------|
| Pilot Roster | A2:H | pilot_id, name, skills, certifications, location, status, assigned_to, available_from |
| Drone Fleet | A2:F | drone_id, model, status, assigned_to, location, maintenance_due |
| Missions | A2:I | mission_id, name, priority, required_skills, required_certifications, location, start_date, end_date, notes |

**Sync Strategy:**
- Read: Load entire sheet into memory
- Write: Update individual rows by ID
- Atomic: Use batch updates for multi-resource operations

---

## Data Flow Examples

### Example 1: Successful Assignment

```
1. User Input: "Assign Sneha to PRJ002 with Drone D003"
   
2. Intent Parser:
   {action: "assign_mission", entities: {...}}
   
3. Coordinator receives intent → Calls Planner
   
4. Planner generates 9-step plan:
   - Load pilots/drones/missions
   - Resolve entities
   - Validate assignment
   - Execute assignment
   - Sync to sheets
   
5. Rules Engine validates:
   ✅ Sneha has required skills
   ✅ D003 is available
   ⚠️  Location mismatch (warning only)
   
6. Execute:
   - Update pilot.assigned_to = "PRJ002"
   - Update pilot.status = "Assigned"
   - Update drone.assigned_to = "PRJ002"
   - Update drone.status = "Assigned"
   
7. Sync to Sheets:
   - Batch update rows for P002 and D003
   
8. Response to user:
   "✅ Successfully assigned Sneha (P002) and Drone D003 to PRJ002"
```

### Example 2: Blocked Assignment with Suggestions

```
1. User Input: "Assign Rohit to PRJ005 with Drone D001"
   
2. Intent parsed successfully
   
3. Coordinator → Planner → Rules Engine
   
4. Validation FAILS:
   ❌ D001 already assigned to PRJ003
   
5. Coordinator triggers Suggestions Engine:
   - Load all available drones
   - Score each against PRJ005 requirements
   - Return top 3 alternatives
   
6. Response to user:
   "❌ Cannot assign: Drone D001 already assigned to PRJ003
   
   💡 Try these available drones instead:
   • D005 (95% match) - Same location, maintenance clear
   • D007 (88% match) - Available, minor location difference
   • D010 (82% match) - Available, different location"
```

### Example 3: Urgent Reassignment

```
1. User Input: "Urgent: Move Drone D001 from PRJ003 to PRJ007"
   
2. Intent: "urgent_reassign"
   
3. Coordinator sets urgent_mode flag
   
4. Modified validation:
   - Skip location warnings
   - Still enforce safety rules
   
5. Execute:
   - Remove D001 from PRJ003
   - Assign D001 to PRJ007
   - Update sheets
   
6. Response:
   "⚠️ Urgent reassignment completed
   Drone D001 moved to PRJ007
   ⚠️ PRJ003 now needs a new drone!"
```

---

## Technology Stack

### Backend
- **Python 3.10** - Core language
- **Google Sheets API v4** - Data storage
- **gspread** - Sheets API wrapper
- **pandas** - Data manipulation
- **python-dotenv** - Environment management

### Frontend
- **Streamlit 1.54.0** - Web framework
- **Plotly** - Interactive charts (Analytics page)
- **Custom CSS** - UI styling with gradients

### AI/LLM (Optional)
- **OpenAI API** or **Anthropic Claude** - Intent parsing
- **Fallback:** Regex-based parser

### Development Tools
- **Git** - Version control
- **conda** - Environment management
- **VS Code** - IDE

---

## Design Patterns Used

### 1. **Deterministic Agent Pattern**
- No randomness in decision-making
- All outputs predictable from inputs
- LLMs only for parsing, not decisions

### 2. **Pipeline Architecture**
- Linear flow: Parse → Plan → Validate → Execute
- Each stage can fail gracefully
- Clear separation of concerns

### 3. **Strategy Pattern** (Validation)
- Pluggable validation rules
- Easy to add/remove rules
- Rules are pure functions

### 4. **Facade Pattern** (Tools Layer)
- Simple interface abstracts complex Sheets API
- Consistent CRUD operations
- Centralized error handling

### 5. **Suggestion/Recommendation Pattern**
- Scoring algorithms for alternatives
- Reusable across different resource types
- User-friendly explanations

---

## Security & Configuration

### Environment Variables (.env)
```bash
SPREADSHEET_ID=1eyZc_vxlgtVCPthtF8RGCg_JLqNEhRT9gbWwnx7jnY0
PILOT_RANGE=Pilot Roster!A2:H
DRONE_RANGE=Drone Fleet!A2:F
MISSION_RANGE=Missions!A2:I
OPENAI_API_KEY=<optional>
```

### Credentials
- `credentials.json` - Google service account key
- **Not in Git** (listed in .gitignore)
- Service account email: skyops-agent@skyops-agent.iam.gserviceaccount.com

### Permissions
- Sheets: Editor access required
- No user OAuth needed (service account)

---

## Deployment Architecture

### Local Development
```
User → Streamlit (localhost:8501) → Python Agent → Sheets API
```

### Production (Streamlit Cloud)
```
User → Streamlit Cloud → Python Agent → Sheets API
    ↓
Secrets stored in Streamlit Cloud dashboard
```

**Requirements:**
- Upload `credentials.json` to Streamlit secrets
- Set environment variables in dashboard
- requirements.txt with all dependencies

---

## Performance Characteristics

### Latency
- **Query operations:** ~500ms (Sheets read + processing)
- **Assignment operations:** ~1.5s (read + validate + write)
- **List operations:** ~300ms (cached)

### Scalability
- **Current:** Handles 100s of resources comfortably
- **Bottleneck:** Google Sheets API rate limits (100 requests/100s)
- **Solution for scale:** Migrate to PostgreSQL + Redis cache

### Reliability
- **Fallback parser:** 100% uptime even if LLM down
- **Retry logic:** Handles transient API failures
- **Validation:** Prevents invalid state

---

## Future Architecture Enhancements

### Short Term (1-2 weeks)
1. **Caching Layer** - Redis for frequently accessed data
2. **Background Jobs** - Celery for async operations
3. **WebSockets** - Real-time updates in UI

### Medium Term (1-2 months)
1. **Database Migration** - PostgreSQL for better queries
2. **API Layer** - REST API for external integrations
3. **Event Sourcing** - Complete audit trail
4. **Multi-tenancy** - Support multiple organizations

### Long Term (3-6 months)
1. **Microservices** - Separate services for pilots/drones/missions
2. **Message Queue** - RabbitMQ/Kafka for event-driven
3. **ML Models** - Predictive assignment recommendations
4. **Mobile App** - React Native for field operations

---

## Monitoring & Observability

### Current State
- Streamlit logs to console
- No structured logging
- Manual error tracking

### Production Needs
- **Logging:** Structured logs with timestamps
- **Metrics:** Prometheus for agent performance
- **Tracing:** OpenTelemetry for request flows
- **Alerts:** PagerDuty for critical failures

---

## Testing Strategy

### Current Coverage
- Manual testing via UI
- No automated tests

### Recommended Test Suite
```
Unit Tests (70% coverage):
- Rules engine (all 9 validation functions)
- Planner (all intent types)
- Entity resolution (pilots/drones/missions)

Integration Tests:
- Google Sheets read/write
- End-to-end assignment flows
- Validation with real data

UI Tests:
- Streamlit page loads
- Chat message flow
- Form submissions
```

---

## Conclusion

SkyOps Agent demonstrates a **pragmatic architecture** that balances:
- ✅ Safety and predictability (deterministic core)
- ✅ User experience (natural language interface)
- ✅ Rapid development (6-hour constraint)
- ✅ Real-world operations (2-way Sheets sync)

The modular design allows independent evolution of each layer, while the deterministic agent pattern ensures operational reliability.
