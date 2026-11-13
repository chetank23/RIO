"""
scripts/seed_sqlite.py
----------------------
Seeds data/campus.db with the standard university project benchmark dataset:
- 6 Batches (A1, A2, A3, B1, B2, B3 across 2 Sections)
- 15 Faculty members with profiles, user logins, and availability
- 10 Campus Rooms (specifically 3 Labs, 2 Seminar Halls, 5 Classrooms)
- 35 Timeslots (5 days MON-FRI × 7 periods P1-P7)
- Realistic Theory courses and Practical/Lab courses (2-3 period requirements)
- Course assignments, faculty availability, resources, and sample bookings
- Baseline Users: Super Admin, Admin, 15 Faculty, and representative Students
"""

from __future__ import annotations

import datetime
from pathlib import Path
import sys

# Ensure repository root is on sys.path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.config import DATABASE_URL, SessionLocal, engine
from backend.core.security import get_password_hash
from backend.models import (
    AcademicCalendar,
    AcademicYear,
    Base,
    Batch,
    Building,
    Course,
    CourseAssignment,
    Department,
    Faculty,
    FacultyAvailability,
    Lab,
    Program,
    Resource,
    ResourceBooking,
    Room,
    Section,
    Semester,
    Student,
    TimeSlot,
    User,
)


def seed_database():
    print(f"[1/6] Initializing SQLite schema on: {DATABASE_URL}")
    db_file = REPO_ROOT / "data" / "campus.db"
    db_file.parent.mkdir(parents=True, exist_ok=True)

    # Recreate tables from declarative models
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Academic Hierarchy
        print("[2/6] Seeding Academic Structure & 6 Batches...")
        dept = Department(department_code="CSE", name="School of Computer Science & Engineering")
        db.add(dept)
        db.flush()

        prog = Program(
            department_id=dept.id,
            program_name="B.Tech Computer Science & Engineering",
            degree="B.Tech",
            duration=4,
        )
        db.add(prog)
        db.flush()

        ay = AcademicYear(
            name="2026-2027",
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2027, 5, 31),
        )
        db.add(ay)
        db.flush()

        sem = Semester(
            academic_year_id=ay.id,
            semester_number=5,
            start_date=datetime.date(2026, 8, 1),
            end_date=datetime.date(2026, 12, 31),
        )
        db.add(sem)
        db.flush()

        sec_a = Section(department_id=dept.id, program_id=prog.id, semester_id=sem.id, section_name="CSE-A", student_count=60)
        sec_b = Section(department_id=dept.id, program_id=prog.id, semester_id=sem.id, section_name="CSE-B", student_count=60)
        db.add_all([sec_a, sec_b])
        db.flush()

        # Exactly 6 batches (A1, A2, A3 for Section A; B1, B2, B3 for Section B)
        batches = [
            Batch(section_id=sec_a.id, batch_name="A1", student_count=20),
            Batch(section_id=sec_a.id, batch_name="A2", student_count=20),
            Batch(section_id=sec_a.id, batch_name="A3", student_count=20),
            Batch(section_id=sec_b.id, batch_name="B1", student_count=20),
            Batch(section_id=sec_b.id, batch_name="B2", student_count=20),
            Batch(section_id=sec_b.id, batch_name="B3", student_count=20),
        ]
        db.add_all(batches)
        db.flush()

        # 2. Campus Facilities: 10 Rooms (3 Labs, 2 Seminar Halls, 5 Classrooms)
        print("[3/6] Seeding Facilities: 10 Rooms (3 Labs, 2 Seminar Halls, 5 Classrooms)...")
        bldg = Building(
            name="Sir M. Visvesvaraya Block",
            code="SMV",
            number_of_floors=4,
        )
        db.add(bldg)
        db.flush()

        rooms = [
            # 3 Labs
            Room(building_id=bldg.id, room_number="LAB-101", room_type="LAB", capacity=40, floor_number=1),
            Room(building_id=bldg.id, room_number="LAB-102", room_type="LAB", capacity=40, floor_number=1),
            Room(building_id=bldg.id, room_number="LAB-103", room_type="LAB", capacity=40, floor_number=1),
            # 2 Seminar Halls
            Room(building_id=bldg.id, room_number="SH-201", room_type="SEMINAR_HALL", capacity=120, floor_number=2),
            Room(building_id=bldg.id, room_number="SH-202", room_type="SEMINAR_HALL", capacity=100, floor_number=2),
            # 5 Classrooms
            Room(building_id=bldg.id, room_number="CR-301", room_type="CLASSROOM", capacity=65, floor_number=3),
            Room(building_id=bldg.id, room_number="CR-302", room_type="CLASSROOM", capacity=65, floor_number=3),
            Room(building_id=bldg.id, room_number="CR-303", room_type="CLASSROOM", capacity=65, floor_number=3),
            Room(building_id=bldg.id, room_number="CR-304", room_type="CLASSROOM", capacity=65, floor_number=3),
            Room(building_id=bldg.id, room_number="CR-305", room_type="CLASSROOM", capacity=65, floor_number=3),
        ]
        db.add_all(rooms)
        db.flush()

        labs = [
            Lab(room_id=rooms[0].id, lab_name="AI & Machine Learning Lab", department_id=dept.id, computer_count=40),
            Lab(room_id=rooms[1].id, lab_name="Data Engineering Lab", department_id=dept.id, computer_count=40),
            Lab(room_id=rooms[2].id, lab_name="Networks & Systems Lab", department_id=dept.id, computer_count=40),
        ]
        db.add_all(labs)
        db.flush()

        # 3. 35 Timeslots: 5 Days × 7 Periods (P1-P7)
        print("[4/6] Seeding 35 Timeslots (5 Days × 7 Periods)...")
        days = ["MON", "TUE", "WED", "THU", "FRI"]
        period_defs = [
            (datetime.time(9, 0), datetime.time(10, 0)),
            (datetime.time(10, 0), datetime.time(11, 0)),
            (datetime.time(11, 15), datetime.time(12, 15)),
            (datetime.time(12, 15), datetime.time(13, 15)),
            (datetime.time(14, 0), datetime.time(15, 0)),
            (datetime.time(15, 0), datetime.time(16, 0)),
            (datetime.time(16, 0), datetime.time(17, 0)),
        ]
        timeslots = []
        for d in days:
            for s_time, e_time in period_defs:
                timeslots.append(
                    TimeSlot(
                        day=d,
                        start_time=s_time,
                        end_time=e_time,
                        slot_type="CLASS",
                    )
                )
        db.add_all(timeslots)
        db.flush()

        # 4. 15 Faculty Members & User Accounts
        print("[5/6] Seeding 15 Faculty Members & Core Users...")
        # Super Admin & Admin
        admin_user = User(
            name="Campus Administrator",
            email="admin@campus.edu",
            password_hash=get_password_hash("admin123"),
            role="ADMIN",
            department_id=dept.id,
            is_active=True,
        )
        superadmin_user = User(
            name="University Super Admin",
            email="superadmin@campus.edu",
            password_hash=get_password_hash("superadmin123"),
            role="ADMIN",
            department_id=dept.id,
            is_active=True,
        )
        db.add_all([admin_user, superadmin_user])
        db.flush()

        faculty_roster = [
            ("Dr. Alan Turing", "alan.turing@campus.edu", "Professor", "Theory of Computation"),
            ("Dr. Grace Hopper", "grace.hopper@campus.edu", "Professor", "Programming Languages"),
            ("Dr. John von Neumann", "john.vonneumann@campus.edu", "Professor", "Computer Architecture"),
            ("Dr. Ada Lovelace", "ada.lovelace@campus.edu", "Associate Professor", "Algorithm Design"),
            ("Dr. Claude Shannon", "claude.shannon@campus.edu", "Associate Professor", "Information Theory"),
            ("Dr. Donald Knuth", "donald.knuth@campus.edu", "Professor", "Analysis of Algorithms"),
            ("Dr. Barbara Liskov", "barbara.liskov@campus.edu", "Associate Professor", "Distributed Systems"),
            ("Dr. Edsger Dijkstra", "edsger.dijkstra@campus.edu", "Associate Professor", "Formal Methods"),
            ("Dr. Tim Berners-Lee", "tim.bernerslee@campus.edu", "Assistant Professor", "Web Engineering"),
            ("Dr. Leslie Lamport", "leslie.lamport@campus.edu", "Assistant Professor", "Concurrent Computing"),
            ("Dr. Andrew Ng", "andrew.ng@campus.edu", "Associate Professor", "Machine Learning"),
            ("Dr. Geoffrey Hinton", "geoffrey.hinton@campus.edu", "Professor", "Deep Learning"),
            ("Dr. Yann LeCun", "yann.lecun@campus.edu", "Associate Professor", "Computer Vision"),
            ("Dr. Yoshua Bengio", "yoshua.bengio@campus.edu", "Associate Professor", "Neural Computation"),
            ("Dr. Fei-Fei Li", "feifei.li@campus.edu", "Associate Professor", "Visual AI"),
        ]

        faculty_entities = []
        for idx, (f_name, f_email, f_desig, f_spec) in enumerate(faculty_roster, start=1):
            u = User(
                name=f_name,
                email=f_email,
                password_hash=get_password_hash("faculty123"),
                role="FACULTY",
                department_id=dept.id,
                is_active=True,
            )
            db.add(u)
            db.flush()

            f = Faculty(
                user_id=u.id,
                department_id=dept.id,
                faculty_id=f"FAC-CSE-{idx:03d}",
                designation=f_desig,
                specialization=f_spec,
                contact_number=f"+91 98450 {idx:04d}",
            )
            db.add(f)
            faculty_entities.append(f)
        db.flush()

        # Faculty availability
        avail_records = []
        for f in faculty_entities:
            for ts in timeslots:
                status = "AVAILABLE"
                pref = 1
                if ts.day in ("TUE", "THU") and ts.start_time.hour in (9, 10, 11):
                    status = "PREFERRED"
                    pref = 3
                avail_records.append(
                    FacultyAvailability(
                        faculty_id=f.id,
                        slot_id=ts.id,
                        availability=status,
                        preference=pref,
                    )
                )
        db.add_all(avail_records)
        db.flush()

        # 5. Courses & Course Assignments
        print("[6/6] Seeding Courses, Assignments, Students & Bookings...")
        courses = [
            # Theory courses (3 lecture hours each)
            Course(department_id=dept.id, course_code="CS501", course_name="Artificial Intelligence", course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
            Course(department_id=dept.id, course_code="CS502", course_name="Database Systems", course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
            Course(department_id=dept.id, course_code="CS503", course_name="Operating Systems", course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
            Course(department_id=dept.id, course_code="CS504", course_name="Computer Networks", course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
            Course(department_id=dept.id, course_code="CS505", course_name="Software Engineering", course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
            # Practical / Lab courses (2 or 3 consecutive hours in lab)
            Course(department_id=dept.id, course_code="CS501L", course_name="AI & Machine Learning Lab", course_type="LAB", credits=2, lecture_hours=0, tutorial_hours=0, practical_hours=3, requires_lab=True),
            Course(department_id=dept.id, course_code="CS502L", course_name="DBMS Laboratory", course_type="LAB", credits=1, lecture_hours=0, tutorial_hours=0, practical_hours=2, requires_lab=True),
            Course(department_id=dept.id, course_code="CS504L", course_name="Computer Networks Lab", course_type="LAB", credits=1, lecture_hours=0, tutorial_hours=0, practical_hours=2, requires_lab=True),
        ]
        db.add_all(courses)
        db.flush()

        assignments = [
            # Section A Theory
            CourseAssignment(course_id=courses[0].id, faculty_id=faculty_entities[10].id, section_id=sec_a.id, batch_id=None),
            CourseAssignment(course_id=courses[1].id, faculty_id=faculty_entities[0].id, section_id=sec_a.id, batch_id=None),
            CourseAssignment(course_id=courses[2].id, faculty_id=faculty_entities[2].id, section_id=sec_a.id, batch_id=None),
            CourseAssignment(course_id=courses[3].id, faculty_id=faculty_entities[4].id, section_id=sec_a.id, batch_id=None),
            CourseAssignment(course_id=courses[4].id, faculty_id=faculty_entities[8].id, section_id=sec_a.id, batch_id=None),
            # Section B Theory
            CourseAssignment(course_id=courses[0].id, faculty_id=faculty_entities[11].id, section_id=sec_b.id, batch_id=None),
            CourseAssignment(course_id=courses[1].id, faculty_id=faculty_entities[1].id, section_id=sec_b.id, batch_id=None),
            CourseAssignment(course_id=courses[2].id, faculty_id=faculty_entities[6].id, section_id=sec_b.id, batch_id=None),
            CourseAssignment(course_id=courses[3].id, faculty_id=faculty_entities[9].id, section_id=sec_b.id, batch_id=None),
            CourseAssignment(course_id=courses[4].id, faculty_id=faculty_entities[7].id, section_id=sec_b.id, batch_id=None),
            # Lab Batches (A1, A2, A3)
            CourseAssignment(course_id=courses[5].id, faculty_id=faculty_entities[12].id, section_id=sec_a.id, batch_id=batches[0].id),
            CourseAssignment(course_id=courses[6].id, faculty_id=faculty_entities[3].id, section_id=sec_a.id, batch_id=batches[1].id),
            CourseAssignment(course_id=courses[7].id, faculty_id=faculty_entities[5].id, section_id=sec_a.id, batch_id=batches[2].id),
            # Lab Batches (B1, B2, B3)
            CourseAssignment(course_id=courses[5].id, faculty_id=faculty_entities[13].id, section_id=sec_b.id, batch_id=batches[3].id),
            CourseAssignment(course_id=courses[6].id, faculty_id=faculty_entities[14].id, section_id=sec_b.id, batch_id=batches[4].id),
            CourseAssignment(course_id=courses[7].id, faculty_id=faculty_entities[4].id, section_id=sec_b.id, batch_id=batches[5].id),
        ]
        db.add_all(assignments)
        db.flush()

        # Representative Students
        for i, b in enumerate(batches, start=1):
            su = User(
                name=f"Student {i}",
                email=f"student{i}@campus.edu",
                password_hash=get_password_hash("student123"),
                role="STUDENT",
                department_id=dept.id,
                is_active=True,
            )
            db.add(su)
            db.flush()

            st = Student(
                user_id=su.id,
                student_id=f"R23CS{i:03d}",
                department_id=dept.id,
                program_id=prog.id,
                semester_id=sem.id,
                section_id=b.section_id,
                batch_id=b.id,
            )
            db.add(st)
        db.flush()

        # Shared Resources & Sample Bookings
        resources = []
        for r in rooms:
            res_type = "LAB" if r.room_type == "LAB" else ("SEMINAR_HALL" if r.room_type == "SEMINAR_HALL" else "EQUIPMENT")
            res = Resource(
                name=f"{r.room_type.replace('_', ' ').title()} - {r.room_number}",
                resource_type=res_type,
                capacity=r.capacity,
                location=f"SMV Block, Floor {r.floor_number}",
                status="ACTIVE",
            )
            db.add(res)
            resources.append(res)
        db.flush()

        # Sample resource bookings (1 approved, 1 pending)
        today = datetime.date.today()
        sample_bookings = [
            ResourceBooking(
                resource_id=resources[3].id,  # SH-201
                requested_by=admin_user.id,
                purpose="AI Technical Symposium",
                date=today + datetime.timedelta(days=3),
                start_time=datetime.time(14, 0),
                end_time=datetime.time(17, 0),
                status="APPROVED",
            ),
            ResourceBooking(
                resource_id=resources[0].id,  # LAB-101
                requested_by=faculty_entities[0].user_id,
                purpose="Hackathon Prep Session",
                date=today + datetime.timedelta(days=4),
                start_time=datetime.time(15, 0),
                end_time=datetime.time(17, 0),
                status="PENDING",
            ),
        ]
        db.add_all(sample_bookings)

        # Academic Calendar
        cal = AcademicCalendar(
            academic_year_id=ay.id,
            date=today + datetime.timedelta(days=10),
            event_type="HOLIDAY",
            description="University Foundation Day",
        )
        db.add(cal)

        db.commit()
        print("\n[SUCCESS] SQLite seed completed successfully!")
        print(f"Database location: {db_file}")

    except Exception as exc:
        db.rollback()
        print(f"[ERROR] Seeding failed: {exc}", file=sys.stderr)
        raise exc
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
