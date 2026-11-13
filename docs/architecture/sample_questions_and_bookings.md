# Comprehensive Benchmark Evaluation Dataset
## 30 Sample Campus Questions & 10 Facility Booking Requests

**Project:** Multi-Agent Campus Assistant & Automated Timetable Engine (RIO-MJP)  
**Evaluation Standard:** Zero-Hallucination SQLite Grounding & Deterministic Booking Lifecycle  

---

## Part 1: 30 Categorized Campus Questions

### A. Student Timetable & Class Schedules (Questions 1–10)
1. *"What is my next class today?"* (Evaluates live time-aware class status for authenticated student).
2. *"Where is my Operating Systems lecture scheduled today?"* (Tests course name lookup and room resolution).
3. *"Show my complete timetable for Thursday."* (Tests single-day full schedule extraction).
4. *"What time is lunch break today?"* (Tests academic interval and break schedule query).
5. *"Do I have any lab sessions scheduled on Wednesday afternoon?"* (Tests lab course and afternoon slot filtering).
6. *"What is my first class tomorrow morning?"* (Tests relative temporal calculation for tomorrow).
7. *"Which room should I go to for Database Systems Lab?"* (Tests lab facility and room code lookup).
8. *"Has my timetable changed this week?"* (Tests disruption and revision change log inspection).
9. *"What subjects am I enrolled in this semester?"* (Tests student enrollment query).
10. *"Show the complete weekly timetable for Section A."* (Tests whole-cohort weekly timetable extraction).

### B. Faculty Teaching & Availability (Questions 11–20)
11. *"Which classes am I assigned to teach this semester?"* (Tests faculty teaching assignment lookup).
12. *"What is Dr. Alan Turing's teaching schedule on Monday?"* (Tests specific faculty schedule query).
13. *"Who is the course instructor for Principles of Federated Learning?"* (Tests course faculty mapping).
14. *"Which faculty members are free on Tuesday period 3 (11:00 AM - 12:00 PM)?"* (Tests faculty availability inspection).
15. *"Show my teaching schedule for today."* (Tests instructor personal daily agenda).
16. *"How many teaching hours am I assigned this week?"* (Tests weekly workload summation).
17. *"Who teaches Computer Networks Lab for Batch A2?"* (Tests batch-specific practical instructor resolution).
18. *"Are there any faculty members available for substitution tomorrow period 2?"* (Tests substitution availability search).
19. *"What are my designated office/available hours this week?"* (Tests faculty availability profile query).
20. *"Who is the class teacher for Section B?"* (Tests section mentorship and administration mapping).

### C. Campus Facilities, Rooms & Administration (Questions 21–30)
21. *"How many computer laboratories are there on campus?"* (Tests facility inventory count filtered by type).
22. *"Where is Room LAB-101 located and what is its capacity?"* (Tests specific facility metadata and capacity lookup).
23. *"Which rooms are free on Friday between 2:00 PM and 4:00 PM?"* (Tests multi-period room availability check).
24. *"Is Seminar Hall SH-201 available on Monday morning?"* (Tests seminar hall schedule clash check).
25. *"List all active classrooms in the Sir M. Visvesvaraya Block."* (Tests building-scoped facility listing).
26. *"How many total active rooms are registered across campus?"* (Tests aggregate facility inventory).
27. *"Is the timetable for Semester 5 currently published or in draft state?"* (Tests timetable version status query).
28. *"What is the capacity of Seminar Hall SH-202?"* (Tests seminar hall seat count verification).
29. *"Are there any public campus events happening today?"* (Tests campus event calendar inspection).
30. *"When do the end-semester examinations begin according to the academic calendar?"* (Tests academic calendar milestone query).

---

## Part 2: 10 Facility Booking Requests & Scenarios

### Scenario 1: Clean Single-Period Lab Reservation
- **Input:** *"Book LAB-102 for tomorrow 2 PM to 4 PM for AI workshop"*
- **Expected Action:** System validates zero clashes on `2026-11-14` between 14:00 and 16:00, generates cryptographic proposal `res_prop_<hex>`, and requires user confirmation.

### Scenario 2: High-Capacity Seminar Hall Booking
- **Input:** *"Reserve Seminar Hall SH-201 on Wednesday from 10:00 AM to 1:00 PM for Guest Lecture on Quantum Computing"*
- **Expected Action:** Checks SH-201 availability, verifies capacity ($\ge 120$ seats), generates proposal token for 3-hour block.

### Scenario 3: Immediate Collision & Automated Alternative Discovery
- **Input:** *"Book LAB-101 for tomorrow 2 PM to 4 PM for Python Bootcamp"*
- **Expected Action:** Detects pre-existing booking for LAB-101. Explains conflict clearly and surfaces viable alternatives (`LAB-102`, `LAB-103`).

### Scenario 4: Natural Language Parameter Modification
- **Follow-up Input:** *"Use Room LAB-102 instead"*
- **Expected Action:** Modifies active proposal, releases LAB-101 hold, validates LAB-102 freshness, and issues updated proposal token.

### Scenario 5: Cryptographic Single-Use Confirmation
- **Input:** *"confirm res_prop_196e7850059cf1b09c18da57274c5f51"*
- **Expected Action:** Consumes single-use token, executes final database freshness check, creates verified booking record (Status: `PENDING`), and assigns Booking ID.

### Scenario 6: Classroom Reservation for Remedial Class
- **Input:** *"Book Classroom CR-103 for Thursday 3:00 PM to 4:00 PM for Data Structures remedial session"*
- **Expected Action:** Checks CR-103 against Section A and B timetables. Verifies no class is scheduled, creates booking proposal.

### Scenario 7: Out-of-Hours Booking Request
- **Input:** *"Book Seminar Hall SH-202 on Saturday from 9:00 AM to 12:00 PM for Hackathon orientation"*
- **Expected Action:** Verifies Saturday facility access policy, confirms zero conflicting events, and generates weekend proposal.

### Scenario 8: User Booking Status Inquiry
- **Input:** *"What is the status of my booking #3?"*
- **Expected Action:** Retrieves Booking #3, displays facility (`LAB-102`), requested interval, and current status (`PENDING` / `APPROVED`).

### Scenario 9: Authorized Booking Cancellation
- **Input:** *"Cancel my booking #3"*
- **Expected Action:** Verifies caller ownership or Admin role, transitions status from `PENDING` to `CANCELLED`, frees time slot, and logs audit trail.

### Scenario 10: Double-Booking Prevention (Race Condition Defense)
- **Input:** Attempting to book the exact same room and interval simultaneously from two sessions.
- **Expected Action:** First transaction succeeds with verified proposal; second transaction is cleanly rejected with a collision explanation and alternative rooms.

