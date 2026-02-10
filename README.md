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
Show me available pilots
List all pilots
Who is available?
```

**Check drone fleet:**
```
Show all drones
List available drones
What drones are in Bangalore?
```

**Check missions:**
```
What missions are active?
Show all projects
List missions
```

### Assignment Commands

**Assign pilot and drone to mission:**
```
Assign Arjun to PRJ001 with Drone D001
Schedule Neha for Project PRJ002 with D003
Book Rohit with Drone D004 for mission PRJ003
```

### Urgent Reassignment

**Move resources between missions:**
```
Urgent: Move Drone D001 from PRJ001 to PRJ002
Reassign Arjun from PRJ001 to PRJ003
Emergency: Transfer D003 from PRJ002 to PRJ001
```

### Add New Resources

**Add resources (shows instructions):**
```
Add a new pilot
Add a new drone
Add a new mission
```

Then add directly to Google Sheet or use the provided Python functions.

---

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd skylark-drones

# Install dependencies
pip install -r requirements.txt

# Set up Google Sheets credentials
# (Add instructions for Google Sheets API setup)

# Run the application
streamlit run app.py
```

## Configuration

1. **Google Sheets Setup**: Configure access to your Google Sheets containing operational data
2. **LLM API**: Set up API keys for the language model (OpenAI, Anthropic, etc.)
3. **Validation Rules**: Customize conflict detection rules in the configuration file

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
skylark-drones/
├── drone_fleet.csv         # Drone inventory and status
├── missions.csv            # Mission scheduling data
├── pilot_roster.csv        # Pilot information and availability
├── app.py                  # Streamlit frontend
├── agent.py                # Deterministic agent loop
├── parser.py               # LLM intent parser
├── validators.py           # Rule-based validation logic
├── sheets_connector.py     # Google Sheets integration
└── README.md              # This file
```

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
