# Weekly Plan & Progress Report — Week 05

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Nov 29, 2026 – Dec 5, 2026  
**Status:** Scheduled  
**Milestone:** 🏆 **Review 2 Milestone** — React + Vite Frontend, Timetable Grid & Conversational UI  

---

## 1. Objectives & Scope
1. Clear **Review 2 (End of Week 5)**:
   - Deliver interactive React + Vite frontend (`frontend/`).
   - Weekly timetable visualization grid with color-coded course/room tiles and filter by Section, Faculty, and Room.
   - Interactive conversational chat interface connected to FastAPI backend (`/chat/message`).
   - Admin console for generating timetables with strategy profiles (Balanced, Faculty Comfort, Room Efficiency, Lab Preference).
2. Wire real-time API integrations between React UI and FastAPI.

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | API Integration & Auth | JWT session management, CORS configuration, API error handlers. |
| **S2 (Operations)** | Admin Console UI | Strategy selector, solver parameters, progress indicators, version browser. |
| **S3 (Agent & NLP)** | Chat UI Component | Streaming/polling chat widget, proposal confirmation pills, markdown renderer. |
| **S4 (Facilities)** | Weekly Timetable Grid | Responsive 5-day × 7-period grid component, room/cohort filter selectors. |
| **S5 (QA & Eval)** | Frontend E2E Testing | Cross-browser testing, accessibility check, production build validation. |

