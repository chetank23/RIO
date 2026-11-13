"""
tests/solver/test_consecutive_labs.py
-------------------------------------
Integration tests verifying that Google OR-Tools CP-SAT scheduler strictly schedules
2-period and 3-period lab sessions as contiguous blocks on the same day in lab facilities.
"""

from __future__ import annotations

from datetime import time
from backend.schemas.timetable_generation import (
    GenerationScope,
    OptimizerInput,
    OptSection,
    OptBatch,
    OptCourse,
    OptCourseAssignment,
    OptFaculty,
    OptFacultyAvailability,
    OptTimeSlot,
    OptRoom,
    OptLab,
)
from solver import TimetableSolver
from solver.verify_timetable import verify_timetable_data


def test_2_period_lab_block_scheduling():
    # 1 Section, 1 Batch, 1 Lab Course with 2 practical hours
    sections = [OptSection(id=1, department_id=1, program_id=1, semester_id=1, student_count=30)]
    batches = [OptBatch(id=1, section_id=1, student_count=30)]
    courses = [
        OptCourse(id=1, department_id=1, course_type="LAB", credits=2, lecture_hours=0, tutorial_hours=0, practical_hours=2, requires_lab=True)
    ]
    assignments = [
        OptCourseAssignment(id=1, course_id=1, faculty_id=1, section_id=1, batch_id=1)
    ]
    faculty = [OptFaculty(id=1, department_id=1, max_weekly_load=10)]
    rooms = [
        OptRoom(id=1, building_id=1, capacity=40, room_type="LAB")
    ]
    labs = [OptLab(id=1, room_id=1, department_id=1)]

    # 4 consecutive periods on Monday: 09:00-10:00, 10:00-11:00, 11:00-12:00, 14:00-15:00
    slots = [
        OptTimeSlot(id=1, day="MON", start_time=time(9, 0), end_time=time(10, 0), slot_type="CLASS"),
        OptTimeSlot(id=2, day="MON", start_time=time(10, 0), end_time=time(11, 0), slot_type="CLASS"),
        OptTimeSlot(id=3, day="MON", start_time=time(11, 0), end_time=time(12, 0), slot_type="CLASS"),
        OptTimeSlot(id=4, day="MON", start_time=time(14, 0), end_time=time(15, 0), slot_type="CLASS"),
    ]
    fa = [
        OptFacultyAvailability(id=i, faculty_id=1, slot_id=i, availability="AVAILABLE", preference=0)
        for i in range(1, 5)
    ]

    opt_input = OptimizerInput(
        scope=GenerationScope(academic_year_id=1, semester_id=1, department_id=1),
        sections=sections,
        batches=batches,
        courses=courses,
        course_assignments=assignments,
        faculty=faculty,
        rooms=rooms,
        labs=labs,
        time_slots=slots,
        faculty_availability=fa,
    )

    solver = TimetableSolver(opt_input=opt_input, time_limit=10, strategy="BALANCED")
    result = solver.solve()

    assert result.feasible is True
    assert len(result.entries) == 2

    # Verify both entries are in Room 1
    assert result.entries[0].room_id == 1
    assert result.entries[1].room_id == 1

    # Verify slots are contiguous (either {1, 2} or {2, 3}; slot 4 cannot be used with 3 because 12:00 != 14:00)
    scheduled_slot_ids = sorted([e.slot_id for e in result.entries])
    assert scheduled_slot_ids in ([1, 2], [2, 3])

    # Verify through independent verifier
    export_entries = [
        {
            "id": idx + 1,
            "course_assignment_id": 1,
            "course_id": 1,
            "course_code": "CS-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "MON",
            "start_time": slots[e.slot_id - 1].start_time.strftime("%H:%M"),
            "end_time": slots[e.slot_id - 1].end_time.strftime("%H:%M"),
            "room_id": e.room_id,
            "room_number": "LAB-101",
            "room_type": "LAB",
            "room_capacity": 40,
            "faculty_id": 1,
            "batch_id": 1,
            "student_count": 30,
        }
        for idx, e in enumerate(result.entries)
    ]
    is_valid, violations, _ = verify_timetable_data(export_entries)
    assert is_valid is True
    assert len(violations) == 0
