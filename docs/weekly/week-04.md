# Weekly Plan & Progress Report — Week 04

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Nov 22, 2026 – Nov 28, 2026  
**Status:** Scheduled  
**Milestone:** Phase 4 — Resource Allocation Agent, Interval Conflicts & Cryptographic Proposals  

---

## 1. Objectives & Scope
1. Implement **Resource Allocation Agent** (`agents/resource_agent/agent.py`) for facilities and room reservations.
2. Build interval conflict detection comparing prospective bookings against both confirmed bookings and scheduled timetable classes.
3. Formulate conflict explanation giving clear diagnostic reasons and proposing alternative available facilities.
4. Implement bounded, single-use, high-entropy proposal tokens (`res_prop_<hex>`) with freshness re-validation at confirmation.

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | Proposal Store & Service | `proposal_store.py`, atomic checkout, TTL expiration, rollback handlers. |
| **S2 (Operations)** | Timetable Overlap | Timetable vs booking collision detection algorithms. |
| **S3 (Agent & NLP)** | Natural Language Parser | `parser.py` (dates, time intervals, room codes, purpose extraction). |
| **S4 (Facilities)** | Alternative Finder | Capacity and facility match scoring (`find_alternative_resources`). |
| **S5 (QA & Eval)** | Booking Test Harness | 10 sample booking requests covering valid, conflict, and modification flows. |

