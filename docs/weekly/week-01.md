# Weekly Progress Report — Week 01

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Nov 1, 2026 – Nov 7, 2026  
**Status:** Completed (100%)  
**Milestone:** Phase 1 — Data Model Foundation, Database Architecture & Benchmark Dataset  

---

## 1. Executive Summary & Sprint Objectives
Week 1 focused on establishing the immutable foundation for the entire project:
1. Designing the relational data model for academic structures, space-time resources, users, and timetable schedules.
2. Implementing **dual-database support** allowing zero-setup local execution using **SQLite** (`data/campus.db`) as the single source of truth while maintaining production readiness for **PostgreSQL**.
3. Authoring the automated seed generator (`scripts/seed_sqlite.py`) to instantiate the required university benchmark dataset.
4. Setting up project governance, test harnesses, and repository standards.

---

## 2. 5-Member Team Division & Contributions

| Role | Teammate | Key Contributions & Artifacts |
|---|---|---|
| **S1: Systems Architect & Backend Lead** | Lead Architect | Dual-database engine configuration (`backend/config.py`), base model setup, JSON/JSONB cross-dialect abstraction (`backend/models/`), SQLAlchemy session factory. |
| **S2: Optimization & Operations Lead** | Operations Lead | Academic structure models (`AcademicYear`, `Semester`, `Department`, `Program`, `Section`, `Batch`), course assignment hierarchy. |
| **S3: Agent & NLP Lead** | Agent Lead | User & RBAC models (`User`, `Student`, `Faculty`), activity logging, query taxonomy alignment. |
| **S4: Full-Stack & Space-Time Lead** | Facilities Lead | Space-time models (`Building`, `Room`, `Lab`, `TimeSlot`, `FacultyAvailability`), resource inventory models (`Resource`, `ResourceBooking`). |
| **S5: Quality Assurance & Evaluation Lead** | QA Lead | Seed data generator (`scripts/seed_sqlite.py`), database integrity verification script, `.gitignore` tracking for `data/campus.db`. |

---

## 3. Tasks Completed

### A. Dual Database Layer (`backend/config.py`)
- Configured SQLAlchemy 2.0 to default to `sqlite:///./data/campus.db` when `DATABASE_URL` is unset.
- Added connection listener for SQLite: `PRAGMA foreign_keys=ON` to enforce strict relational referential integrity.
- Configured `connect_args={"check_same_thread": False}` for multi-threaded FastAPI compatibility.
- Maintained seamless fallback to PostgreSQL (`postgresql+psycopg://`) when connection string is provided.
- Abstracted PostgreSQL-specific `JSONB` fields to `JSON().with_variant(JSONB, "postgresql")` across `backend/models/`.

### B. University Benchmark Dataset Seed (`scripts/seed_sqlite.py`)
Populated `data/campus.db` with the mandatory benchmark configuration:
- **6 Batches:** Section A (`A1`, `A2`, `A3`) and Section B (`B1`, `B2`, `B3`) with 20 students per batch (60 students per section).
- **15 Faculty Members:** Profiles across Artificial Intelligence, Systems, Theory, and Networks with predefined availability.
- **10 Campus Rooms:**
  - 3 Dedicated Computer Laboratories (`LAB-101`, `LAB-102`, `LAB-103`, capacity 40 each).
  - 2 Seminar Halls (`SH-201`, capacity 120; `SH-202`, capacity 100).
  - 5 Standard Classrooms (`CR-101` through `CR-105`, capacity 65 each).
- **35 Weekly Timeslots:** 5 working days (MON–FRI) × 7 periods per day (09:00 to 17:00, including Lunch break).
- **Curriculum:** 8 Courses (5 Theory courses requiring 3 lecture hours/week; 3 Lab courses requiring 2–3 practical hours/week).
- **Seed Bookings & Users:** Verified student, faculty, and administrator accounts; sample bookings in pending and confirmed states.

---

## 4. Test & Verification Results

```bash
$ python scripts/seed_sqlite.py
======================================================================
 RIO-MJP SQLITE SEEDING & BENCHMARK DATASET GENERATION
======================================================================
Database Target: /Users/wopsy/programming/rio/RIO/data/campus.db
[1/9] Initializing schema metadata...
[2/9] Creating academic hierarchy...
[3/9] Creating rooms and laboratories...
[4/9] Creating weekly timeslots (MON-FRI x 7 periods)...
[5/9] Creating faculty accounts and availability profiles...
[6/9] Creating student cohorts and section batches...
[7/9] Creating academic courses and teaching assignments...
[8/9] Creating bookable facilities and sample bookings...
[9/9] Verifying database integrity...
      - Academic Years: 1
      - Semesters: 1
      - Departments: 1
      - Sections: 2
      - Batches: 6
      - Faculty: 15
      - Rooms: 10 (Labs: 3, Seminar Halls: 2, Classrooms: 5)
      - Time Slots: 35
      - Courses: 8
      - Course Assignments: 16
      - Resources: 10
      - Bookings: 2
======================================================================
SEEDING COMPLETED SUCCESSFULLY: 100% RELATIONAL INTEGRITY VERIFIED
======================================================================
```

---

## 5. Blockers Encountered & Resolutions

| Issue | Root Cause | Resolution |
|---|---|---|
| SQLite `Index already exists` crash | Model classes declared duplicate index definitions via both column-level `index=True` and table-level `__table_args__`. | Removed redundant column-level index declarations in `workflow.py`, `placements.py`, and `events.py`. |
| Missing Foreign Key cascades in SQLite | SQLite defaults to `foreign_keys=OFF`. | Registered `@event.listens_for(engine, "connect")` emitting `PRAGMA foreign_keys=ON;`. |
| `JSONB` unsupported on SQLite | PostgreSQL-only type imported directly into declarative models. | Updated to `JSON().with_variant(JSONB, "postgresql")` in `chat.py` and `workflow.py`. |

---

## 6. Next Week (Week 02) Objectives
- Build Google OR-Tools CP-SAT scheduler in canonical `solver/` package.
- Formulate hard constraints (no faculty clash, no room clash, no batch clash, room capacity >= class size).
- Enforce 2–3 period contiguous laboratory blocks.
- Build independent, zero-dependency verifier script (`solver/verify_timetable.py`).
- Implement pre-solve mathematical infeasibility diagnostics (`solver/presolve.py`).
- Clear **Review 1 Milestone**.

