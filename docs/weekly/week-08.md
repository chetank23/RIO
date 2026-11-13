# Weekly Plan & Progress Report — Week 08

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Dec 20, 2026 – Dec 26, 2026  
**Status:** Scheduled  
**Milestone:** Phase 8 — End-to-End System Integration, Event Management & Placement Module  

---

## 1. Objectives & Scope
1. Integrate campus event management and placement drive scheduling into the unified assistant.
2. Ensure event venue reservations trigger calendar clash checks against academic timetables.
3. Conduct end-to-end integration across LangGraph, FastAPI, SQLite, and React.
4. Verify cross-agent handoffs between Supervisor, Query Agent, Resource Agent, and Scheduling Agent.

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | End-to-End Wiring | Graph routing optimization, state persistence across turns. |
| **S2 (Operations)** | Placement Modules | Placement drive schema, eligibility filters, interview room bookings. |
| **S3 (Agent & NLP)** | Event Conversational Flow | Multi-turn event draft creation and approval via conversation. |
| **S4 (Facilities)** | Multi-Venue Booking | Complex bookings spanning multiple rooms or entire blocks. |
| **S5 (QA & Eval)** | Full Regression Suite | End-to-end integration test execution (`tests/integration/`). |

