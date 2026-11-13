# System Architecture & Multi-Agent Orchestration

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Architecture Pattern:** Layered Multi-Agent System with Shared State & Independent Verifier  

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph ClientLayer["Frontend Client Layer (React 18 + Vite)"]
        ChatUI["Conversational Assistant Chat UI"]
        GridUI["Weekly Timetable Grid (Filter by Section/Faculty/Room)"]
        AdminConsole["Admin Timetable Generation & Strategy Console"]
        BookingPanel["Facility Booking & Proposal Confirmation Panel"]
    end

    subgraph APILayer["Backend API Layer (FastAPI + Pydantic)"]
        AuthRouter["/auth (JWT Authentication & RBAC)"]
        ChatRouter["/chat/message (Multi-Agent Dispatch)"]
        TimetableRouter["/timetable (Generate, Preview, Publish)"]
        ResourceRouter["/resources (Facilities, Bookings, Proposals)"]
    end

    subgraph AgentLayer["Multi-Agent Framework (LangGraph)"]
        Supervisor["LangGraph Supervisor Node (Intent Classifier)"]
        QueryAgent["Query Agent (Database Grounded Q&A)"]
        ResourceAgent["Resource Allocation Agent (Interval Clash & Proposal Store)"]
        SchedulingAgent["Scheduling Agent (Strategy Profiling & Diagnostics)"]
        TemporalAnchor["Temporal Anchor (Date/Time/Day Context Injection)"]
        LLMGateway["Multi-Provider LLM Gateway (Groq / Gemini / Ollama / Anthropic)"]
    end

    subgraph SolverLayer["Optimization & Verification Layer (CP-SAT)"]
        Presolve["Pre-Solve Infeasibility Diagnostics (solver/presolve.py)"]
        CPSATSolver["Google OR-Tools CP-SAT Solver (backend/optimizer/)"]
        ConsecutiveLabs["Consecutive 2-3 Period Lab Block Enforcer"]
        SoftConstraints["Soft Constraints (Faculty B2B, Afternoon Labs, Gaps)"]
        IndependentVerifier["Zero-Dependency Independent Verifier CLI (solver/verify_timetable.py)"]
    end

    subgraph DataLayer["Storage Layer (Single Source of Truth)"]
        SQLiteDB[("SQLite Database: data/campus.db (Default)")]
        PostgresDB[("PostgreSQL Database (Production Target)")]
        ExportJSON["data/generated_timetable.json (Independent Audit Output)"]
    end

    %% Client to API
    ChatUI --> ChatRouter
    GridUI --> TimetableRouter
    AdminConsole --> TimetableRouter
    BookingPanel --> ResourceRouter

    %% API to Multi-Agent & Solver
    ChatRouter --> Supervisor
    TimetableRouter --> CPSATSolver
    ResourceRouter --> ResourceAgent

    %% Agent Layer Internal
    Supervisor --> TemporalAnchor
    TemporalAnchor --> QueryAgent
    TemporalAnchor --> ResourceAgent
    TemporalAnchor --> SchedulingAgent

    QueryAgent --> LLMGateway
    ResourceAgent --> LLMGateway
    SchedulingAgent --> LLMGateway

    %% Solver Flow
    SchedulingAgent --> Presolve
    Presolve --> CPSATSolver
    CPSATSolver --> ConsecutiveLabs
    CPSATSolver --> SoftConstraints
    CPSATSolver --> ExportJSON
    ExportJSON --> IndependentVerifier

    %% Database Connections
    QueryAgent --> SQLiteDB
    ResourceAgent --> SQLiteDB
    CPSATSolver --> SQLiteDB
    AuthRouter --> SQLiteDB
    SQLiteDB -.-> PostgresDB
```

---

## 2. Multi-Agent Interaction & Execution Flows

### A. Grounded Query Execution Flow
```mermaid
sequenceDiagram
    autonumber
    actor User as Student / Faculty / Admin
    participant ChatUI as React Chat UI
    participant FastAPI as /chat/message Router
    participant Supervisor as LangGraph Supervisor
    participant QueryAgent as Query Agent
    participant LLM as Groq / Gemini / Ollama
    participant Tools as Database Query Tools
    participant DB as SQLite data/campus.db

    User->>ChatUI: "What is my next class today?"
    ChatUI->>FastAPI: POST /chat/message { message, user_token }
    FastAPI->>Supervisor: invoke(AgentState)
    Supervisor->>QueryAgent: route to query_agent (intent: QUERY)
    QueryAgent->>QueryAgent: Inject live datetime (e.g. 2026-11-13 Friday)
    QueryAgent->>LLM: Tool Call Selection with Temporal Anchor
    LLM-->>QueryAgent: return tool_name: "get_class_status"
    QueryAgent->>Tools: execute_tool("get_class_status", user)
    Tools->>DB: SELECT timetable_entries WHERE day='FRI' AND time >= current_time
    DB-->>Tools: Return { course: 'CS301', room: 'CR-101', start: '14:00' }
    Tools-->>QueryAgent: Raw relational data
    QueryAgent->>QueryAgent: format_grounded_response(raw_data)
    QueryAgent-->>Supervisor: AgentState updated (sources: [Academic Timetable])
    Supervisor-->>FastAPI: Final response payload
    FastAPI-->>ChatUI: JSON response with verified answer and sources
    ChatUI-->>User: "Your next class is CS301 (Operating Systems) at 14:00 in Room CR-101."
```

### B. Facility Booking & Cryptographic Proposal Flow
```mermaid
sequenceDiagram
    autonumber
    actor User as Faculty Member
    participant ChatUI as React Chat UI
    participant ResourceAgent as Resource Agent
    participant ProposalStore as Proposal Store
    participant DB as SQLite data/campus.db

    User->>ChatUI: "Book LAB-102 for tomorrow 2 PM to 4 PM for AI workshop"
    ChatUI->>ResourceAgent: Parse date, time, facility, purpose
    ResourceAgent->>DB: Interval Clash Check (Bookings & Timetable)
    DB-->>ResourceAgent: 0 conflicts detected
    ResourceAgent->>ProposalStore: generate proposal token (res_prop_196e7850...)
    ProposalStore-->>ResourceAgent: Stored with 10-minute TTL
    ResourceAgent-->>ChatUI: Return proposal summary + confirmation token
    ChatUI-->>User: Displays "Resource Booking Proposal: LAB-102 on 2026-11-14 (14:00-16:00)"
    User->>ChatUI: Clicks "Confirm & Submit Booking"
    ChatUI->>ResourceAgent: "confirm res_prop_196e7850..."
    ResourceAgent->>ProposalStore: consume_proposal(token, user_id)
    ProposalStore-->>ResourceAgent: Validated (single-use token consumed)
    ResourceAgent->>DB: Re-verify freshness & INSERT INTO resource_bookings (status='PENDING')
    DB-->>ResourceAgent: Booking #3 created
    ResourceAgent-->>ChatUI: "Booking #3 submitted successfully (Status: PENDING)"
```

---

## 3. Mathematical Optimization & Independent Verification Architecture

1. **Pre-Solve Infeasibility Diagnostics (`solver/presolve.py`):**
   - Evaluates whether $\sum \text{Required Hours} \le \text{Total Slots}$ across each section, batch, and faculty member.
   - Evaluates whether $\text{Class Size} \le \max(\text{Room Capacity})$.
   - Evaluates total lab hours vs available lab rooms $\times$ slots (Pigeonhole principle).

2. **Google OR-Tools CP-SAT Solver (`backend/optimizer/timetable_solver.py`):**
   - Decision variables: $x(a, h, r, t) \in \{0, 1\}$.
   - Contiguous lab blocks: Boolean block choice variables for 2-hour and 3-hour practical courses enforcing $(t, t+1)$ or $(t, t+1, t+2)$ on the same day in the same laboratory room.
   - Objective: Minimizes weighted penalty terms for faculty back-to-back periods ($> 2$ periods), morning lab slots, faculty schedule gaps, student gaps, and room changes.

3. **Standalone Independent Verifier CLI (`solver/verify_timetable.py`):**
   - Independent verification component written with **zero external dependencies** (Python standard library only).
   - Reads any exported schedule JSON and systematically asserts:
     - Hard Constraint 1: $\forall i \neq j, \text{faculty}_i == \text{faculty}_j \implies \neg \text{overlap}(t_i, t_j)$
     - Hard Constraint 2: $\forall i \neq j, \text{room}_i == \text{room}_j \implies \neg \text{overlap}(t_i, t_j)$
     - Hard Constraint 3: $\forall i \neq j, \text{cohort}_i == \text{cohort}_j \implies \neg \text{overlap}(t_i, t_j)$
     - Hard Constraint 4: $\forall i, \text{capacity}(\text{room}_i) \ge \text{size}(\text{cohort}_i)$
     - Hard Constraint 5: Practical sessions are strictly contiguous and housed in lab facilities.

