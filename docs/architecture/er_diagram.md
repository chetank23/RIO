# Relational Database Architecture & Entity-Relationship Model

**Database:** SQLite (`data/campus.db`) / PostgreSQL  
**Engine:** SQLAlchemy 2.0 Declarative ORM  
**Referential Integrity:** Enforced via `PRAGMA foreign_keys = ON;`  

---

## 1. Complete Entity-Relationship Diagram

```mermaid
erDiagram
    ACADEMIC_YEAR ||--o{ SEMESTER : contains
    ACADEMIC_YEAR ||--o{ TIMETABLE_VERSION : scopes
    DEPARTMENT ||--o{ PROGRAM : offers
    DEPARTMENT ||--o{ FACULTY : employs
    DEPARTMENT ||--o{ SECTION : organizes
    DEPARTMENT ||--o{ COURSE : manages
    DEPARTMENT ||--o{ ROOM : operates
    SEMESTER ||--o{ SECTION : schedules
    PROGRAM ||--o{ SECTION : enrolls
    SECTION ||--o{ BATCH : subdivides
    SECTION ||--o{ STUDENT : contains
    BATCH ||--o{ STUDENT : assigns

    COURSE ||--o{ COURSE_ASSIGNMENT : defines
    FACULTY ||--o{ COURSE_ASSIGNMENT : teaches
    SECTION ||--o{ COURSE_ASSIGNMENT : takes
    BATCH ||--o{ COURSE_ASSIGNMENT : attends_lab

    BUILDING ||--o{ ROOM : houses
    ROOM ||--o{ LAB : equips
    ROOM ||--o{ RESOURCE : registers
    ROOM ||--o{ TIMETABLE_ENTRY : hosts

    TIME_SLOT ||--o{ TIMETABLE_ENTRY : times
    COURSE_ASSIGNMENT ||--o{ TIMETABLE_ENTRY : schedules
    TIMETABLE_VERSION ||--o{ TIMETABLE_ENTRY : versions

    USER ||--o{ STUDENT : identifies
    USER ||--o{ FACULTY : identifies
    USER ||--o{ RESOURCE_BOOKING : requests
    RESOURCE ||--o{ RESOURCE_BOOKING : reserves

    ACADEMIC_YEAR {
        int id PK
        string name
        date start_date
        date end_date
    }

    SEMESTER {
        int id PK
        int academic_year_id FK
        int semester_number
        date start_date
        date end_date
    }

    DEPARTMENT {
        int id PK
        string department_code UK
        string name
    }

    PROGRAM {
        int id PK
        int department_id FK
        string code UK
        string name
    }

    SECTION {
        int id PK
        int department_id FK
        int program_id FK
        int semester_id FK
        string name
        int student_count
    }

    BATCH {
        int id PK
        int section_id FK
        string name
        int student_count
    }

    COURSE {
        int id PK
        int department_id FK
        string code UK
        string name
        string course_type
        int credits
        int lecture_hours
        int tutorial_hours
        int practical_hours
        boolean requires_lab
    }

    COURSE_ASSIGNMENT {
        int id PK
        int course_id FK
        int faculty_id FK
        int section_id FK
        int batch_id FK
    }

    BUILDING {
        int id PK
        string code UK
        string name
    }

    ROOM {
        int id PK
        int building_id FK
        int department_id FK
        string room_number UK
        string room_type
        int capacity
    }

    LAB {
        int id PK
        int room_id FK
        int department_id FK
        string lab_type
    }

    TIME_SLOT {
        int id PK
        string day
        time start_time
        time end_time
        string slot_type
    }

    TIMETABLE_VERSION {
        int id PK
        int academic_year_id FK
        int semester_id FK
        int department_id FK
        string version_tag
        string status
        float quality_score
    }

    TIMETABLE_ENTRY {
        int id PK
        int version_id FK
        int course_assignment_id FK
        int room_id FK
        int slot_id FK
        string hour_type
    }

    USER {
        int id PK
        string email UK
        string hashed_password
        string role
        string full_name
        boolean is_active
    }

    FACULTY {
        int id PK
        int user_id FK
        int department_id FK
        string employee_code UK
        string designation
        int max_weekly_load
    }

    STUDENT {
        int id PK
        int user_id FK
        int section_id FK
        int batch_id FK
        string srn UK
        string roll_number
    }

    RESOURCE {
        int id PK
        int room_id FK
        string name
        string resource_type
        int capacity
        boolean is_bookable
    }

    RESOURCE_BOOKING {
        int id PK
        int resource_id FK
        int user_id FK
        date booking_date
        time start_time
        time end_time
        string purpose
        string status
    }
```

---

## 2. Relational Integrity Rules
1. **Academic Hierarchy Cascade:** Deleting an `AcademicYear` cascades to related `Semester` records. Sections strictly map to a single `Department`, `Program`, and `Semester`.
2. **Subdivision Invariant:** A `Batch` strictly belongs to a parent `Section`. The sum of student counts across batches in a section does not exceed the section's total student count.
3. **Lab Exclusivity:** Course assignments marked `PRACTICAL` must link to a `Batch` and can only be scheduled into rooms flagged with `room_type = 'LAB'` and indexed in `LAB`.
4. **Referential Constraints:** All foreign keys are indexed. SQLite enforces foreign keys on every connection via `PRAGMA foreign_keys = ON;`.

