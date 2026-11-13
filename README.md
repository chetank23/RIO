# RIO — Multi-Agent Campus Assistant & Automated Timetable Engine

[![Python Version](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![OR-Tools CP-SAT](https://img.shields.io/badge/Google%20OR--Tools-CP--SAT-4285F4.svg)](https://developers.google.com/optimization)
[![LangGraph](https://img.shields.io/badge/LangGraph-Multi--Agent-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![SQLite](https://img.shields.io/badge/Database-SQLite%203%20%28Default%29-003B57.svg)](https://sqlite.org/)
[![Independent Verifier](https://img.shields.io/badge/Independent%20Verifier-0%20Violations%20Passed-success.svg)](solver/verify_timetable.py)

---

## 1. Executive Summary & Project Overview

**RIO** is an enterprise-grade academic operations platform designed for university institutions. It seamlessly unites:
1. **Automated Mathematical Timetabling:** Powered by **Google OR-Tools CP-SAT**, generating mathematically provable, collision-free weekly schedules in seconds across multiple sections, faculty cohorts, classrooms, and specialized laboratories.
2. **Deterministic Independent Verification:** A standalone, zero-external-dependency verifier (`solver/verify_timetable.py`) that strictly validates all 5 core university hard constraints separately from the solver output.
3. **Multi-Agent Conversational Campus Assistant:** Built on **LangGraph**, providing role-based query answering, resource allocation, and disruption management with live date/time awareness grounded exclusively in the campus database (zero hallucinations).
4. **Dual-Database Architecture:** Defaults to zero-setup **SQLite** (`data/campus.db`) for immediate evaluation, while supporting high-concurrency **PostgreSQL** in production.

---

## 2. Mandatory Tech Stack & Architecture

| Layer | Primary Technology | Purpose & Implementation |
|---|---|---|
| **Database** | SQLite (`data/campus.db`) | Single source of truth. Zero-setup local evaluation, relational foreign key enforcement (`PRAGMA foreign_keys=ON`). Dual support for PostgreSQL. |
| **Optimization Solver** | Google OR-Tools CP-SAT (`solver/`, `backend/optimizer/`) | Constraint programming engine solving hard constraints (no faculty/room/batch clashes) and soft constraints (faculty back-to-back penalties, afternoon labs). |
| **Independent Verifier** | Python Standard Library CLI (`solver/verify_timetable.py`) | Zero-dependency independent audit tool verifying timetable outputs separately from the solver. |
| **Agent Framework** | LangGraph (`agents/`) | Stateful multi-agent graph with Supervisor dispatch, Query Agent, and Resource Allocation Agent. |
| **Backend API** | Python 3.12 + FastAPI + Pydantic | RESTful endpoints, JWT authentication, server-side RBAC, and WebSocket event dispatch. |
| **LLM Gateway** | Groq / Gemini / Ollama / Anthropic (`agents/common/llm_client.py`) | Multi-provider LLM gateway with live temporal injection (current date, time, weekday) and offline deterministic fallback. |
| **Frontend UI** | React 18 + Vite + TypeScript (`frontend/`) | Interactive weekly timetable grid, admin generation console, and conversational assistant chat interface. |

---

## 3. Weekly Progress Table (10-Week Project Schedule)

| Week | Sprint Window | Deliverables & Milestones | Status | Review Log |
|:---:|:---:|---|:---:|:---:|
| **01** | Nov 1 – Nov 7, 2026 | Data Model Architecture, Dual SQLite/PostgreSQL Engine, Benchmark Seed Dataset (6 batches, 15 faculty, 10 rooms, 35 slots). | 🟢 Completed | [Week 01 Report](docs/weekly/week-01.md) |
| **02** | Nov 8 – Nov 14, 2026 | **Review 1 Milestone:** Canonical `solver/` package, CP-SAT scheduler, consecutive 2–3 period lab blocks, soft constraints, pre-solve checks, Independent Verifier CLI. | 🟢 Completed | [Week 02 Report](docs/weekly/week-02.md) |
| **03** | Nov 15 – Nov 21, 2026 | LangGraph Shared State, Supervisor Node, Multi-Provider LLM Gateway (Groq, Gemini, Ollama), live temporal prompt injection. | 🟡 In Progress | [Week 03 Report](docs/weekly/week-03.md) |
| **04** | Nov 22 – Nov 28, 2026 | Resource Allocation Agent, interval collision detection, natural language parser, single-use cryptographic proposals (`res_prop_<hex>`). | ⚪ Scheduled | [Week 04 Report](docs/weekly/week-04.md) |
| **05** | Nov 29 – Dec 5, 2026 | **Review 2 Milestone:** React + Vite Frontend, 5-day × 7-period Weekly Timetable Grid, Conversational Assistant UI, Admin Console. | ⚪ Scheduled | [Week 05 Report](docs/weekly/week-05.md) |
| **06** | Dec 6 – Dec 12, 2026 | Timetable Disruption Handling, Minimal Perturbation Optimization, Slot Locking, Ripple Rescheduling Proposals. | ⚪ Scheduled | [Week 06 Report](docs/weekly/week-06.md) |
| **07** | Dec 13 – Dec 19, 2026 | Role-Based Access Control (Admin, Faculty, Student), Privacy Data Masking, Faculty Substitution Workflow. | ⚪ Scheduled | [Week 07 Report](docs/weekly/week-07.md) |
| **08** | Dec 20 – Dec 26, 2026 | Campus Events & Placement Modules, multi-venue booking, end-to-end multi-agent integration. | ⚪ Scheduled | [Week 08 Report](docs/weekly/week-08.md) |
| **09** | Dec 27, 2026 – Jan 2, 2027 | **Review 3 Milestone:** System Performance Benchmarking, Concurrency Stress Testing, Scalability Profiling. | ⚪ Scheduled | [Week 09 Report](docs/weekly/week-09.md) |
| **10** | Jan 3 – Jan 9, 2027 | **Final Major Project Defense:** Comprehensive Project Report, 5-minute video demonstration, release tagging. | ⚪ Scheduled | [Week 10 Report](docs/weekly/week-10.md) |

---

## 4. 5-Member Team Work Division

```
                      ┌───────────────────────────────────────────────┐
                      │             Student 1 (Team Lead)             │
                      │         Systems Architect & Backend Lead      │
                      └──────────────────────┬────────────────────────┘
                                             │
      ┌──────────────────────┬───────────────┴───────────────┬──────────────────────┐
      │                      │                               │                      │
┌─────┴────────────────┐ ┌───┴──────────────────┐ ┌──────────┴───────────┐ ┌──────┴────────────────┐
│      Student 2       │ │      Student 3       │ │      Student 4       │ │      Student 5         │
│ Optimization Lead &  │ │ AI, NLP & LangGraph  │ │ Full-Stack & UI Lead │ │ QA, Testing & Verifier │
│ Operations Engineer  │ │ Conversational Agent │ │ Space-Time Model     │ │ Audit & Benchmarking   │
└──────────────────────┘ └──────────────────────┘ └──────────────────────┘ └────────────────────────┘
```

1. **Student 1 (Lead Architect & Systems Engineer):** Overall system architecture, dual-database layer, FastAPI backend routing, JWT security, and LangGraph supervisor workflow.
2. **Student 2 (Optimization & Operations Lead):** Google OR-Tools CP-SAT formulation, consecutive lab block variables, disruption service, and solver scoring metrics.
3. **Student 3 (Agent & NLP Lead):** Conversational prompt engineering, live date/time anchor injection, multi-provider LLM gateway (Groq/Gemini/Ollama), and query agent grounded formatter.
4. **Student 4 (Full-Stack & Facilities Lead):** React + Vite frontend, interactive weekly timetable grid, space-time models, and resource booking interface.
5. **Student 5 (Quality Assurance & Evaluation Lead):** Standalone Independent Verifier CLI, pre-solve diagnostic suite, test harnesses, and automated audit benchmarking.

---

## 5. Zero-Setup Evaluation Quickstart

This repository is pre-configured for instant evaluation with **zero external infrastructure** (no PostgreSQL or cloud setup required).

### Prerequisites
- Python 3.12+
- Node.js 18+ (for frontend)

### Step 1: Environment Setup
```bash
# Clone the repository
git clone https://github.com/chetank23/RIO.git
cd RIO

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install backend dependencies
pip install -r requirements.txt
```

### Step 2: Seed the SQLite Benchmark Dataset
Generates 6 batches, 15 faculty, 10 rooms (3 labs, 2 seminar halls), 35 timeslots, courses, and sample bookings in `data/campus.db`:
```bash
python scripts/seed_sqlite.py
```

### Step 3: Run the CP-SAT Timetable Solver & Independent Verifier
Executes pre-solve checks, solves the weekly timetable, exports `data/generated_timetable.json`, and verifies all 5 hard constraints:
```bash
python scripts/generate_and_verify_timetable.py
```

### Step 4: Run the Independent Verifier CLI Standalone
Audit any generated timetable JSON using the zero-dependency verifier:
```bash
python -m solver.verify_timetable data/generated_timetable.json
```
*Expected Output:*
```
======================================================================
 RIO-MJP INDEPENDENT TIMETABLE VERIFIER REPORT
======================================================================
File Inspected:       data/generated_timetable.json
Total Entries:        44
Hard Constraints:     🟢 0 VIOLATIONS (PASSED)
----------------------------------------------------------------------
  ✅ Constraint 1: Zero Faculty Clashes Verified
  ✅ Constraint 2: Zero Room Clashes Verified
  ✅ Constraint 3: Zero Section & Batch Clashes Verified
  ✅ Constraint 4: Room Capacity >= Cohort Size Verified
  ✅ Constraint 5: Consecutive 2-3 Period Lab Blocks Verified
======================================================================
STATUS: VALID TIMETABLE CANDIDATE (EXIT CODE 0)
```

### Step 5: Run Automated Tests
```bash
pytest tests/solver/ tests/api/test_optimizer.py tests/api/test_optimizer_soft_constraints.py tests/database/test_database_safety.py
```
*Result: 29 passed in < 1s.*

### Step 6: Start the Backend & Frontend Servers
```bash
# Terminal 1: Launch FastAPI Backend (runs on http://127.0.0.1:8000)
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload

# Terminal 2: Launch React Frontend (runs on http://localhost:5173)
cd frontend
npm install
npm run dev
```

---

## 6. Architecture & Evaluation Documentation

- **[Relational ER Diagram](docs/architecture/er_diagram.md):** Complete Mermaid entity-relationship diagram of all SQLite tables.
- **[System Architecture](docs/architecture/system_architecture.md):** Layered architecture diagram and multi-agent interaction sequence flows.
- **[Benchmark Evaluation Dataset](docs/architecture/sample_questions_and_bookings.md):** 30 categorized campus questions and 10 facility booking scenarios.
- **[Project Audit & Remediation Status](docs/PROJECT_AUDIT_STATUS.md):** Forensic audit report detailing compliance across Review 1 and Review 2.

---

## 7. Non-Negotiable Ground Rules Compliance

1. **Solver First, Agents Second:** The data model and CP-SAT scheduler are completed and verified before UI interactions.
2. **Zero Hallucination / Single Source of Truth:** One SQLite database (`data/campus.db`) is the sole authority; no agent answers from pre-trained memory.
3. **Independent Verification:** `solver/verify_timetable.py` evaluates schedules completely independent of solver code with 0 violations.
4. **Hard Constraints Strictly Enforced:** Zero faculty clash, zero room clash, zero section/batch clash, room capacity $\ge$ class size.
5. **Consecutive Lab Blocks:** Practical lab sessions are strictly scheduled as contiguous 2–3 period blocks in dedicated laboratories.
6. **Live Date/Time Injection:** Live timestamp context is injected into every system instruction to resolve relative temporal references.
