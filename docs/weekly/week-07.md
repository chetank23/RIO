# Weekly Plan & Progress Report — Week 07

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Sprint Window:** Dec 13, 2026 – Dec 19, 2026  
**Status:** Scheduled  
**Milestone:** Phase 7 — Role-Based Access Control, Privacy Masking & Personalized Views  

---

## 1. Objectives & Scope
1. Implement fine-grained server-side **RBAC** for Super Admin, Admin, Faculty, and Student roles.
2. Ensure students can only access their enrolled subjects, section schedule, and personal bookings.
3. Mask sensitive instructor information (e.g. personal contact numbers, other faculty leave records).
4. Implement faculty teaching dashboard and room booking approvals.

---

## 2. 5-Member Team Work Division

| Teammate | Focus Area | Planned Deliverables |
|---|---|---|
| **S1 (Architect)** | Security Middleware | JWT claims inspection, route dependencies, HTTP 403 Forbidden enforcement. |
| **S2 (Operations)** | Faculty Portal | View assigned courses, submit availability preferences, accept substitution requests. |
| **S3 (Agent & NLP)** | Tool RBAC Filters | `allowed_roles` checks in `QUERY_TOOL_DEFINITIONS` and `execute_tool`. |
| **S4 (Facilities)** | Booking Approval UI | Admin workflow for reviewing, approving, or rejecting pending facility bookings. |
| **S5 (QA & Eval)** | Security Tests | Authorization test suite in `tests/api/test_auth_rbac.py`. |

