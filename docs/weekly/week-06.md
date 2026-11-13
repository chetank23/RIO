# Weekly Plan & Progress Report — Week 06

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Dec 6, 2026 – Dec 12, 2026  
**Status:** Scheduled  
**Milestone:** Phase 6 — Timetable Disruption Handling & Minimal Perturbation Rescheduling  

---

## 1. Objectives & Scope
1. Implement timetable disruption handling when faculty call in sick or rooms undergo emergency maintenance.
2. Formulate **minimal perturbation optimization** penalizing deviation from the baseline published timetable.
3. Support slot locking (`locked_assignments`) and ripple effects (`allow_ripple=True`).
4. Generate conversational explanation of affected cohorts and reschedule proposals.

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | Disruption Service | `backend/services/disruption_service.py`, versioning and draft diffing. |
| **S2 (Operations)** | Perturbation Solver | Minimal perturbation objective weighting ($W_{\text{slot}} = 500$, $W_{\text{room}} = 200$). |
| **S3 (Agent & NLP)** | Disruption Dialogue | Conversational disruption intake ("Dr. Turing is unavailable on Wednesday"). |
| **S4 (Facilities)** | Room Maintenance | Emergency room out-of-order flag and auto-substitution routing. |
| **S5 (QA & Eval)** | Rescheduling Tests | Disruption test suite in `tests/api/test_disruptions.py`. |

