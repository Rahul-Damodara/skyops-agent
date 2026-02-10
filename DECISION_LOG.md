# Decision Log - SkyOps Agent: Drone Operations Coordinator

**Project:** Drone Operations Coordinator AI Agent  
**Date:** February 10, 2026  
**Author:** Rahul Damodara  
**Time Constraint:** 6 hours  

---

## 1. Key Assumptions Made

### Data Structure & Formats
- **Date Format:** Assumed DD-MM-YYYY format for all dates (available_from, maintenance_due, start_date, end_date)
- **CSV to Google Sheets:** Assumed existing CSV data would be uploaded to Google Sheets as-is without schema changes
- **Empty Fields:** Assumed various representations of "no assignment" (–, -, empty, special characters) needed handling
- **Pilot Status Values:** Assumed three states: "Available", "Assigned", "On Leave" are sufficient
- **Drone Status Values:** Assumed three states: "Available", "Assigned", "Maintenance"

### Operational Assumptions
- **Single Assignment:** Assumed pilots and drones can only be assigned to one project at a time (no part-time/shared assignments)
- **Skill Matching:** Assumed exact string matching for skills (case-insensitive) - no fuzzy matching or skill hierarchies
- **Location Proximity:** Treated location mismatch as a warning, not a blocker (assuming resources can travel)
- **Priority Hierarchy:** Assumed Urgent > High > Standard > default priority levels
- **Certification Requirements:** Assumed ALL required certifications must be met (no partial matches)

### User Interaction
- **Natural Language Queries:** Assumed users would use simple, imperative sentences
- **Context Retention:** Assumed no need for multi-turn conversation memory (each query is independent)
- **Error Tolerance:** Assumed users may use variations of commands (assign/allocate/schedule treated equally)

---

## 2. Trade-offs & Rationale

### Architecture: Deterministic Agent vs. Pure LLM

**Decision:** Hybrid approach with deterministic core and optional LLM parsing

**Rationale:**
- **Safety First:** Operational decisions (assignments, validations) must be 100% predictable and auditable
- **LLM Role:** Limited to intent parsing only - never makes decisions about assignments
- **Fallback Strategy:** Simple keyword-based parser as fallback when LLM unavailable → ensures system always works
- **Trade-off:** Less conversational flexibility vs. guaranteed operational correctness

**What We Gave Up:**
- Natural follow-up questions ("which Arjun?" if multiple exist)
- Contextual understanding across multiple queries
- Suggestive recommendations ("How about assigning Rohit instead?")

**What We Gained:**
- Zero risk of hallucinated assignments
- Complete audit trail of all decisions
- Predictable behavior for testing and debugging
- No dependency on LLM for core functionality

---

### Tech Stack Choices

**1. Streamlit vs. Custom Web Framework**

**Chose:** Streamlit  
**Why:**
- Rapid prototyping (6-hour constraint)
- Built-in chat interface with state management
- Native Python integration (no JS context switching)
- Easy deployment to Streamlit Cloud

**Trade-off:** Less UI flexibility vs. faster time-to-prototype

**2. Google Sheets vs. Database**

**Chose:** Google Sheets  
**Why:**
- Requirement specified Google Sheets
- Non-technical users can view/edit data directly
- No database setup/maintenance overhead
- Built-in backup and version history
- Familiar interface for operations teams

**Trade-off:** Limited query capabilities vs. accessibility for end users

**3. Simple State Management vs. Redis/Database**

**Chose:** In-memory Python dict (agent_state)  
**Why:**
- Stateless operation model (each query independent)
- No external dependencies to deploy
- Sufficient for prototype scope
- Enables urgent_mode flags for special workflows

**Trade-off:** State lost on restart vs. simplicity and speed

---

### Validation Strategy: Blocking vs. Warnings

**Decision:** Two-tier validation system

**Blocking Issues (Hard Failures):**
- Double-booking (pilot/drone already assigned)
- Missing required skills
- Missing required certifications
- Drone in maintenance
- Maintenance due during mission period

**Warnings (Soft Failures):**
- Location mismatch (resource and mission in different cities)
- Pilot available_from date after mission start
- Date parsing failures

**Rationale:**
- Operations team knows when location travel is feasible → warning, not blocker
- Safety-critical requirements (skills, certs) are hard blocks
- Allows informed decisions rather than rigid enforcement

---

## 3. Interpretation of "Urgent Reassignments"

### Problem Understanding
The requirement stated: *"The agent should help coordinate urgent reassignments"* without specific definition.

### My Interpretation

**Definition:** Urgent reassignment = moving a pilot and/or drone from one mission to another due to:
- Emergency client request
- Equipment failure requiring drone swap
- Pilot unavailability (illness, emergency)
- Higher-priority mission taking precedence

### Implementation Approach

**1. Separate Intent:** Created 'urgent_reassign' as distinct from regular 'assign_mission'

**2. Special Workflow:**
```
User: "Urgent: Move Drone D001 from PRJ001 to PRJ002"
↓
System:
1. Sets urgent_mode flag in agent state
2. Loads current assignments
3. Validates target mission compatibility
4. Executes reassignment (removes from old, assigns to new)
5. Updates Google Sheets
6. Warns that old mission needs new assignment
7. Clears urgent_mode
```

**3. Validation Relaxation:**
- Still enforces skill/cert matching (safety)
- Still blocks if drone in maintenance (safety)
- Location warnings shown but don't block (urgency overrides)

**4. Audit Trail:**
- All urgent actions logged with timestamp
- Leaves "orphaned" mission visible (requires manual follow-up)
- Clear warning messages about downstream impacts

### Alternative Interpretations Considered

**Option A:** Auto-suggest replacement resources  
*Rejected:* LLM should not make operational suggestions

**Option B:** Override all validations in urgent mode  
*Rejected:* Safety requirements (skills/certs) are never optional

**Option C:** Require explicit authorization/password  
*Rejected:* Out of scope for prototype; would implement in production

---

## 4. What I'd Do Differently With More Time

### Immediate Improvements (1-2 additional hours)

**1. Enhanced Entity Extraction**
- Handle ambiguous names ("Which Arjun - P001 or P005?")
- Support partial IDs ("Drone 01" → D001)
- Extract dates from natural language ("next Monday")

**2. Batch Operations**
- "Assign all available pilots with Mapping skills to missions in Bangalore"
- Bulk status updates

**3. Reporting & Analytics**
- Resource utilization dashboard
- Conflict frequency metrics
- Assignment history timeline

### Major Features (1-2 additional days)

**4. Multi-turn Conversations**
- Maintain context across queries
- Follow-up questions and clarifications
- Undo/redo functionality

**5. Smart Recommendations**
- Suggest best pilot-drone-mission matches
- Predict conflicts before they occur
- Optimization algorithms for assignments

**6. Advanced Conflict Resolution**
- Propose alternative solutions when validation fails
- "Arjun lacks Thermal skill - but Sneha is available and qualified"
- Priority-based auto-reassignment

**7. Notification System**
- Email/SMS alerts for urgent situations
- Pilot notifications for new assignments
- Client updates on resource changes

**8. Audit & Compliance**
- Complete change history with rollback
- User authentication and role-based access
- Compliance reports (who assigned what, when)

### Production Readiness (1-2 weeks)

**9. Testing Suite**
- Unit tests for all validation rules
- Integration tests for Google Sheets sync
- End-to-end scenario tests
- Load testing for concurrent users

**10. Error Handling**
- Retry logic for API failures
- Graceful degradation when Sheets unavailable
- Better error messages with suggested fixes

**11. Security**
- OAuth instead of service account for user-level access
- API rate limiting
- Input sanitization and validation
- Secrets management (not .env files)

**12. Scalability**
- Move to proper database (PostgreSQL)
- Caching layer (Redis)
- Background job processing (Celery)
- WebSocket for real-time updates

---

## 5. Technical Debt & Known Limitations

### Current Limitations

1. **No data validation on input:** Assumes Google Sheets data is well-formed
2. **Single-user assumption:** No concurrency control for simultaneous edits
3. **No transaction support:** Partial failures could leave inconsistent state
4. **Limited rollback:** Can't undo completed assignments
5. **Simple intent parsing:** Keyword-based fallback is brittle for complex queries
6. **No caching:** Every query reads entire sheets (slow for large datasets)
7. **English-only:** No internationalization support

### Edge Cases Not Fully Handled

1. **Time zones:** All dates assumed to be in local time
2. **Overlapping dates:** Mission date ranges not deeply validated
3. **Partial availability:** Can't handle "available for 3 days out of 5"
4. **Pilot preferences:** No consideration of pilot location preference
5. **Equipment compatibility:** Doesn't validate if pilot certified for specific drone model

---

## 6. Success Metrics & Evaluation

### What Success Looks Like

**Functional:**
- ✅ All CRUD operations work (query, assign, add, update)
- ✅ 100% of specified edge cases handled correctly
- ✅ 2-way Google Sheets sync operational
- ✅ Conflict detection catches all specified scenarios

**User Experience:**
- ✅ Natural language queries understood correctly
- ✅ Clear error messages guide user to fix issues
- ✅ Fast response time (<2 seconds per query)

**Code Quality:**
- ✅ Separation of concerns (LLM layer, business logic, data layer)
- ✅ Documented architecture and decision rationale
- ✅ Git history shows incremental, logical progress

### Measured Against Requirements

| Requirement | Status | Notes |
|-------------|--------|-------|
| Roster management | ✅ Complete | Query, view, update with sync |
| Assignment tracking | ✅ Complete | Match, track, reassign |
| Drone inventory | ✅ Complete | Query, track, flag issues |
| Conflict detection | ✅ Complete | All 4 edge cases handled |
| Urgent reassignment | ✅ Complete | Implemented with validation |
| Google Sheets sync | ✅ Complete | Bidirectional read/write |
| Conversational UI | ✅ Complete | Streamlit chat interface |
| Hosted prototype | ⚠️ Deployable | Streamlit Cloud ready |

---

## Conclusion

This assignment required balancing **rapid prototyping** with **production-quality decision-making**. The core architectural choice - deterministic agent with optional LLM parsing - reflects prioritization of **safety and auditability** over conversational sophistication.

The 6-hour constraint forced ruthless prioritization: every feature implemented is essential to the core user workflow. Features like analytics, recommendations, and multi-user support were consciously deferred.

The result is a functional, testable prototype that demonstrates the feasibility of AI-augmented operations coordination while maintaining human oversight and control.

**Key learning:** In operational systems, predictability and auditability trump conversational flexibility. The LLM should augment, not replace, deterministic business logic.
