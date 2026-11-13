"""
tests/solver/test_presolve.py
-----------------------------
Unit tests for solver/presolve.py mathematical infeasibility diagnostics.
Verifies pre-solve detection of impossible configurations before CP-SAT invocation.
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
from solver.presolve import run_presolve_checks


def create_minimal_dataset():
    sections = [OptSection(id=1, department_id=1, program_id=1, semester_id=1, student_count=40)]
    batches = [OptBatch(id=1, section_id=1, student_count=20)]
    courses = [
        OptCourse(id=1, department_id=1, course_type="THEORY", credits=3, lecture_hours=3, tutorial_hours=0, practical_hours=0, requires_lab=False),
        OptCourse(id=2, department_id=1, course_type="LAB", credits=2, lecture_hours=0, tutorial_hours=0, practical_hours=2, requires_lab=True),
    ]
    assignments = [
        OptCourseAssignment(id=1, course_id=1, faculty_id=1, section_id=1, batch_id=None),
        OptCourseAssignment(id=2, course_id=2, faculty_id=2, section_id=1, batch_id=1),
    ]
    faculty = [
        OptFaculty(id=1, department_id=1, max_weekly_load=16),
        OptFaculty(id=2, department_id=1, max_weekly_load=16),
    ]
    rooms = [
        OptRoom(id=1, building_id=1, capacity=60, room_type="CLASSROOM"),
        OptRoom(id=2, building_id=1, capacity=30, room_type="LAB"),
    ]
    labs = [OptLab(id=1, room_id=2, department_id=1)]
    slots = [
        OptTimeSlot(id=i, day="MON", start_time=time(9 + (i - 1), 0), end_time=time(10 + (i - 1), 0), slot_type="CLASS")
        for i in range(1, 8)
    ]
    fa = [
        OptFacultyAvailability(id=1, faculty_id=1, slot_id=1, availability="AVAILABLE", preference=0),
        OptFacultyAvailability(id=2, faculty_id=1, slot_id=2, availability="AVAILABLE", preference=0),
        OptFacultyAvailability(id=3, faculty_id=1, slot_id=3, availability="AVAILABLE", preference=0),
        OptFacultyAvailability(id=4, faculty_id=2, slot_id=4, availability="AVAILABLE", preference=0),
        OptFacultyAvailability(id=5, faculty_id=2, slot_id=5, availability="AVAILABLE", preference=0),
    ]

    return OptimizerInput(
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


def test_presolve_clean_dataset_passes():
    dataset = create_minimal_dataset()
    res = run_presolve_checks(dataset)
    assert res.feasible is True
    assert len(res.issues) == 0


def test_presolve_room_capacity_exceeded():
    dataset = create_minimal_dataset()
    # Section has 100 students, but max classroom capacity is only 60
    dataset.sections[0].student_count = 100
    res = run_presolve_checks(dataset)
    assert res.feasible is False
    assert any("exceeding maximum classroom capacity" in issue for issue in res.issues)


def test_presolve_section_hours_exceed_weekly_slots():
    dataset = create_minimal_dataset()
    # 7 available slots, but course requires 10 lecture hours
    dataset.courses[0].lecture_hours = 10
    res = run_presolve_checks(dataset)
    assert res.feasible is False
    assert any("exceeding total weekly slots" in issue for issue in res.issues)


def test_presolve_faculty_unavailability_overload():
    dataset = create_minimal_dataset()
    # Faculty #1 requires 3 hours, but has only 1 available slot
    dataset.faculty_availability = [
        OptFacultyAvailability(id=1, faculty_id=1, slot_id=1, availability="AVAILABLE", preference=0)
    ]
    res = run_presolve_checks(dataset)
    assert res.feasible is False
    assert any("requires 3 teaching hours but is only available for 1 slots" in issue for issue in res.issues)
