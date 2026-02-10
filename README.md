# SkyOps Agent – Drone Operations Coordinator

An intelligent agentic AI system designed to coordinate drone operations, manage pilot assignments, and ensure mission readiness through automated conflict detection and resource management.

## Overview

SkyOps Agent is a drone operations coordinator that combines natural language understanding with deterministic rule-based logic to manage drone fleets, pilot rosters, and mission scheduling. The system ensures operational safety and efficiency by detecting conflicts, validating assignments, and supporting urgent resource reassignment.

## Key Features

### 🎯 Core Capabilities
- **Natural Language Interface**: Streamlit-based frontend for intuitive user interaction
- **Intent Parsing**: LLM-powered extraction of user intent and entities from natural language queries
- **Deterministic Agent Loop**: Rule-based planning and execution engine for operational decisions
- **Conflict Detection**: Automated identification of scheduling conflicts, skill mismatches, and maintenance issues
- **Resource Management**: Real-time tracking of drones, pilots, and missions
- **Urgent Reassignment**: Support for emergency resource reallocation

### 🛡️ Safety & Validation
- **Double-booking Prevention**: Ensures no pilot or drone is assigned to multiple missions simultaneously
- **Skill Matching**: Validates pilot certifications against drone requirements
- **Maintenance Tracking**: Monitors drone availability and maintenance schedules
- **Rule-Based Decision Making**: All operational decisions are made through deterministic logic, never by the LLM

## Architecture

### Design Principles
1. **LLM Role**: Limited to parsing user intent and extracting entities (pilot names, drone IDs, mission details)
2. **Operational Logic**: All assignments, validations, and conflict resolution handled by deterministic rule-based code
3. **Data Source**: Google Sheets serves as the single source of truth for all operational data
4. **Agent Loop**: Deterministic planning and execution cycle ensures predictable and auditable operations

### System Components
```
┌─────────────────────┐
│  Streamlit Frontend │
│  (User Interface)   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   LLM Parser        │
│  (Intent & Entity)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Deterministic      │
│  Agent Loop         │
│  (Planning & Logic) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Google Sheets      │
│  (Source of Truth)  │
└─────────────────────┘
```

## Data Structure

The system manages three primary data sources:

### 1. Pilot Roster (`pilot_roster.csv`)
- Pilot information and certifications
- Availability status
- Skill levels and drone type qualifications

### 2. Drone Fleet (`drone_fleet.csv`)
- Drone specifications and capabilities
- Maintenance status
- Current location and availability

### 3. Missions (`missions.csv`)
- Mission details and requirements
- Scheduled time slots
- Assigned pilots and drones
- Mission status

## Conflict Detection

The system automatically detects and reports:

- **Double-booking**: Pilot or drone assigned to overlapping missions
- **Skill Mismatch**: Pilot lacks required certification for assigned drone type
- **Maintenance Conflicts**: Drone scheduled for mission during maintenance window
- **Availability Issues**: Resource not available at mission time
- **Capacity Limits**: Drone payload or range limitations

## Usage Examples

### Assign a Pilot to a Mission
```
User: "Assign John to Mission Alpha with Drone 101"
System: [Validates availability, skills, drone status]
        ✓ Assignment successful
```

### Detect Conflicts
```
User: "Schedule Sarah for Mission Bravo at 2PM"
System: ⚠ Conflict detected: Sarah already assigned to Mission Charlie at 2PM
```

### Emergency Reassignment
```
User: "Urgent: Reassign Drone 203 from Mission Delta to Mission Echo"
System: [Validates emergency protocol]
        ✓ Reassignment complete
        ℹ Mission Delta marked for new drone assignment
```

## Usage Examples

### Query Commands

**Check pilot availability:**
```
User: "Show me available pilots"

Agent Response:
📋 Current Pilots:
┌──────────┬───────┬────────────┬──────────┬──────────────────────┐
│ pilot_id │ name  │ location   │ status   │ drone_type_certified │
├──────────┼───────┼────────────┼──────────┼──────────────────────┤
│ P001     │ Arjun │ Bangalore  │ Active   │ Multirotor          │
│ P002     │ Neha  │ Mumbai     │ Inactive │ Fixed-wing          │
└──────────┴───────┴────────────┴──────────┴──────────────────────┘
```

**Other pilot queries:**
```
"List all pilots"
"Who is available?"
"Show pilots in Bangalore"
```

**Check drone fleet:**
```
User: "Show all drones"

Agent Response:
🚁 Current Drones:
┌──────────┬────────────┬────────────┬────────────┐
│ drone_id │ drone_type │ status     │ location   │
├──────────┼────────────┼────────────┼────────────┤
│ D001     │ Multirotor │ Available  │ Bangalore  │
│ D002     │ Fixed-wing │ Maintenance│ Delhi      │
└──────────┴────────────┴────────────┴────────────┘
```

**Other drone queries:**
```
"List available drones"
"What drones are in Bangalore?"
"Show drones under maintenance"
```

**Check missions:**
```
User: "What missions are active?"

Agent Response:
📅 Active Missions:
┌────────────┬──────────────┬────────────┬───────────────┬───────────────┐
│ mission_id │ mission_name │ location   │ pilot_assigned│ drone_assigned│
├────────────┼──────────────┼────────────┼───────────────┼───────────────┤
│ PRJ001     │ Survey North │ Bangalore  │ Arjun         │ D001          │
│ PRJ002     │ Inspection   │ Mumbai     │ None          │ None          │
└────────────┴──────────────┴────────────┴───────────────┴───────────────┘
```

### Assignment Commands

**Successful assignment:**
```
User: "Assign Arjun to PRJ001 with Drone D001"

Agent validates:
✅ Arjun is available
✅ D001 is available
✅ Arjun is certified for Multirotor drones
✅ D001 is in same location as mission

Agent Response:
✅ Assignment Successful!

Mission PRJ001 has been assigned:
  • Pilot: Arjun (P001)
  • Drone: D001 (Multirotor)
  • Location: Bangalore
  • Scheduled: 2024-01-15 10:00

Updated Google Sheets ✓
```

**Other assignment patterns:**
```
"Schedule Neha for Project PRJ002 with D003"
"Book Rohit with Drone D004 for mission PRJ003"
"Assign pilot P001 and drone D002 to PRJ001"
```

**Assignment with conflict:**
```
User: "Assign Arjun to PRJ002 with Drone D001"

Agent Response:
❌ Assignment Blocked - Conflicts Detected:

BLOCKING ISSUES:
  ⚠ Pilot Arjun is already assigned to PRJ001
  ⚠ Drone D001 is already assigned to PRJ001

Please resolve these conflicts before proceeding.
```

**Assignment with skill mismatch:**
```
User: "Assign Neha to PRJ001 with Drone D001"

Agent Response:
❌ Assignment Blocked - Conflicts Detected:

BLOCKING ISSUES:
  ⚠ Pilot Neha (certified: Fixed-wing) cannot operate 
    Multirotor drone D001
    
Suggestion: Assign a pilot certified for Multirotor drones.
```

**Assignment with maintenance conflict:**
```
User: "Assign Arjun to PRJ003 with Drone D002"

Agent Response:
❌ Assignment Blocked - Conflicts Detected:

BLOCKING ISSUES:
  ⚠ Drone D002 is currently under maintenance
  
Suggestion: Choose a drone with status 'Available'.
```

### Urgent Reassignment

**Move drone between missions:**
```
User: "Urgent: Move Drone D001 from PRJ001 to PRJ002"

Agent validates:
✅ D001 is currently assigned to PRJ001
✅ D001 is compatible with PRJ002
✅ No conflicts with reassignment

Agent Response:
✅ Urgent Reassignment Successful!

Drone D001 has been moved:
  FROM: Mission PRJ001 (Survey North)
  TO:   Mission PRJ002 (Inspection)

⚠ WARNING: Mission PRJ001 now needs a new drone assignment!

Updated Google Sheets ✓
```

**Move pilot between missions:**
```
User: "Reassign Arjun from PRJ001 to PRJ003"

Agent Response:
✅ Urgent Reassignment Successful!

Pilot Arjun has been moved:
  FROM: Mission PRJ001
  TO:   Mission PRJ003

⚠ WARNING: Mission PRJ001 now needs a new pilot assignment!

Updated Google Sheets ✓
```

**Other urgent patterns:**
```
"Emergency: Transfer D003 from PRJ002 to PRJ001"
"Urgent reassign: Move pilot P001 from PRJ001 to PRJ002"
```

### Add New Resources

**Add new pilot:**
```
User: "Add a new pilot"

Agent Response:
To add a new pilot, add a row to the pilot_roster sheet with these columns:
  • pilot_id (e.g., P005)
  • name
  • contact
  • license_number
  • certification_level
  • drone_type_certified
  • location
  • availability_status
  • experience_years
  • current_assignment (leave empty initially)
  • last_flight_date

Or use Python function:
  add_new_pilot(name="Kavya", contact="9876543210", ...)
```

**Add new drone:**
```
User: "Add a new drone"

Agent Response:
To add a new drone, add a row to the drone_fleet sheet with:
  • drone_id (e.g., D005)
  • drone_type
  • status
  • location
  • payload_capacity_kg
  • battery_status
  • last_maintenance_date

Or use Python function:
  add_new_drone(drone_type="Multirotor", status="Available", ...)
```

**Add new mission:**
```
User: "Add a new mission"

Agent Response:
To add a new mission, add a row to the missions sheet with:
  • mission_id (e.g., PRJ004)
  • mission_name
  • location
  • scheduled_date
  • scheduled_time
  • pilot_assigned (initially None)
  • drone_assigned (initially None)
  • mission_status
  • estimated_duration_hrs

Or use Python function:
  add_new_mission(mission_name="New Survey", location="Delhi", ...)
```

### Real-World Scenarios

**Scenario 1: Morning briefing**
```
User: "Show me today's active missions"
Agent: [Lists all missions scheduled for today with assignments]

User: "Are all drones available?"
Agent: [Lists drone status, highlights any in maintenance]

User: "Who is available for emergency response?"
Agent: [Lists pilots with 'Active' status and no current assignment]
```

**Scenario 2: Schedule new mission**
```
User: "Create a survey mission in Pune for tomorrow at 10 AM"
Agent: [Explains how to add mission to Google Sheet]

User: [Adds mission PRJ004 to sheet]

User: "Assign Rohit to PRJ004 with Drone D003"
Agent: ✅ [Validates and assigns resources]
```

**Scenario 3: Emergency reallocation**
```
User: "D001's battery just died - move it from PRJ001 to maintenance"
Agent: [Updates drone status to Maintenance]

User: "Urgent: Reassign D002 from PRJ003 to PRJ001"
Agent: ✅ [Moves drone, warns about PRJ003 needing new drone]

User: "Show available drones in Bangalore"
Agent: [Lists D003 and D004 as options]

User: "Assign D003 to PRJ003"
Agent: ✅ [Completes fallback assignment]
```

---

## Installation

### Prerequisites
- Python 3.10 or higher
- Git
- Google Cloud Project with Sheets API enabled
- Google Sheets with drone operations data

### Step 1: Clone Repository
```bash
git clone https://github.com/Rahul-Damodara/skyops-agent.git
cd skyops-agent
```

### Step 2: Set Up Python Environment
```bash
# Create conda environment (recommended)
conda create -n skyops python=3.10
conda activate skyops

# Or use venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Google Sheets Access

1. **Create Google Cloud Service Account**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing
   - Enable Google Sheets API
   - Create Service Account credentials
   - Download JSON key file

2. **Share Google Sheet**:
   - Open your Google Sheet
   - Share with service account email (e.g., `skyops-agent@project.iam.gserviceaccount.com`)
   - Grant "Editor" permissions

3. **Save Credentials**:
   - Save the JSON key file as `credentials.json` in project root
   - **Important**: Never commit this file to Git (already in `.gitignore`)

### Step 5: Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Google Sheets Configuration (REQUIRED)
SPREADSHEET_ID=your-spreadsheet-id-here
PILOT_RANGE=pilot_roster!A:K
DRONE_RANGE=drone_fleet!A:G
MISSION_RANGE=missions!A:I

# LLM API Keys (OPTIONAL - fallback to keyword parser if not set)
OPENAI_API_KEY=your-openai-key-here
ANTHROPIC_API_KEY=your-anthropic-key-here
```

**To get your Spreadsheet ID**: Copy from the URL between `/d/` and `/edit`
```
https://docs.google.com/spreadsheets/d/SPREADSHEET_ID_HERE/edit
```

### Step 6: Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## Configuration

### Google Sheets Data Format

Your Google Sheet should have three tabs:

**1. pilot_roster** (columns A-K):
- pilot_id, name, contact, license_number, certification_level, drone_type_certified, location, availability_status, experience_years, current_assignment, last_flight_date

**2. drone_fleet** (columns A-G):
- drone_id, drone_type, status, location, payload_capacity_kg, battery_status, last_maintenance_date

**3. missions** (columns A-I):
- mission_id, mission_name, location, scheduled_date, scheduled_time, pilot_assigned, drone_assigned, mission_status, estimated_duration_hrs

### LLM Configuration (Optional)

The system works in two modes:

1. **With LLM** (OpenAI/Anthropic): Natural language understanding for complex queries
2. **Without LLM** (Keyword-based): Pattern matching for standard operations

Both modes use **deterministic rules** for all operational decisions. The LLM only helps with intent parsing.

---

## Deployment to Streamlit Cloud

### Prerequisites
- GitHub account with your repository pushed
- Streamlit Cloud account (free at [streamlit.io/cloud](https://streamlit.io/cloud))
- Google Sheets with service account access configured

### Step-by-Step Deployment

#### 1. Prepare Your Repository
```bash
git add .
git commit -m "Ready for deployment"
git push origin main
```

#### 2. Create Streamlit Cloud App
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app"
4. Select repository: `Rahul-Damodara/skyops-agent`
5. Branch: `main`
6. Main file: `app.py`

#### 3. Configure Secrets
Click "Advanced settings" → "Secrets" and add:

```toml
# .streamlit/secrets.toml
[gcp_service_account]
type = "service_account"
project_id = "skyops-agent"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "skyops-agent@skyops-agent.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"

SPREADSHEET_ID = "your-spreadsheet-id"
PILOT_RANGE = "pilot_roster!A:K"
DRONE_RANGE = "drone_fleet!A:G"
MISSION_RANGE = "missions!A:I"
```

> **Note**: Copy all fields from your `credentials.json` file into the `gcp_service_account` section

#### 4. Deploy
- Click "Deploy"
- Wait 2-3 minutes for build completion
- Your app will be live at: `https://your-app-name.streamlit.app`

#### 5. Verify Deployment
Test these commands:
- ✅ "Show me all pilots"
- ✅ "Assign Arjun to PRJ001 with Drone D001"
- ✅ "Urgent: Move Drone D001 from PRJ001 to PRJ002"

### Troubleshooting Deployment

**Error: "Module not found"**
- Ensure `requirements.txt` includes all dependencies
- Check Python version compatibility (3.10+)

**Error: "Google Sheets API access denied"**
- Verify service account email has Editor access to your Google Sheet
- Check credentials are properly formatted in secrets.toml

**App crashes on startup**
- Check Streamlit Cloud logs in the dashboard
- Verify `SPREADSHEET_ID` is correct
- Ensure all environment variables are set

---

## Project Structure

```
skyops-agent/
├── agent/
│   ├── coordinator.py      # Main agent loop and execution engine
│   ├── planner.py          # Intent-to-plan converter
│   ├── rules.py            # Deterministic validation rules
│   └── memory.py           # Simple state management
├── tools/
│   ├── sheets.py           # Google Sheets API wrapper
│   ├── pilots.py           # Pilot roster management
│   ├── drones.py           # Drone fleet management
│   └── missions.py         # Mission scheduling management
├── app.py                  # Streamlit frontend interface
├── intent_parser.py        # LLM/keyword-based intent parser
├── requirements.txt        # Python dependencies
├── credentials.json        # Google service account (DO NOT COMMIT)
├── .env                    # Environment variables (DO NOT COMMIT)
├── README.md              # This file
├── DECISION_LOG.md        # Architecture decisions and trade-offs
├── IMPLEMENTATION_CHECKLIST.md  # Development progress tracking
├── drone_fleet.csv        # Local drone data (optional)
├── missions.csv           # Local mission data (optional)
└── pilot_roster.csv       # Local pilot data (optional)
```

### Key Files

- **app.py**: Streamlit chat interface with data display and execution tracking
- **agent/coordinator.py**: Main orchestration logic with execution functions
- **agent/planner.py**: Converts user intents into actionable plans
- **agent/rules.py**: Validation engine with 7 blocking rules + 2 warnings
- **tools/sheets.py**: Google Sheets read/write operations
- **intent_parser.py**: Natural language → structured intent conversion

## Important Notes

⚠️ **Critical Design Constraint**: The LLM is **NEVER** used to make operational decisions. Its role is strictly limited to:
- Understanding user intent
- Extracting entities from natural language
- Formatting responses for users

All assignment logic, conflict detection, and validation are performed by deterministic, rule-based code to ensure:
- Predictability
- Auditability
- Safety
- Compliance with operational procedures

## Development

### Adding New Validation Rules
1. Define rule logic in `validators.py`
2. Register rule in the agent loop
3. Add test cases for new scenarios

### Extending Conflict Detection
1. Identify new conflict types
2. Implement detection logic
3. Update conflict resolution protocols

## License

[Add your license here]

## Contact

For questions or support, contact the Skylark Drones development team.

---

**Built for safe, efficient, and intelligent drone operations management.**
