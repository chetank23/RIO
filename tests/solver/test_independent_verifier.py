"""
tests/solver/test_independent_verifier.py
------------------------------------------
Unit tests for the independent, zero-backend-dependency timetable verifier.
Verifies that all 5 non-negotiable hard constraints are strictly validated
and that any violations are accurately flagged.
"""

from __future__ import annotations

import datetime
from solver.verify_timetable import verify_timetable_data


def test_valid_timetable_passes():
    entries = [
        {
            "id": 1,
            "day": "MON",
            "start_time": "09:00",
            "end_time": "10:00",
            "faculty_id": 1,
            "faculty_name": "Dr. Alan Turing",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 1,
            "section_name": "Section A",
            "batch_id": None,
            "student_count": 50,
            "course_id": 101,
            "course_code": "CS101",
            "course_type": "THEORY",
            "hour_type": "THEORY",
        },
        {
            "id": 2,
            "day": "MON",
            "start_time": "10:00",
            "end_time": "11:00",
            "faculty_id": 2,
            "faculty_name": "Dr. Grace Hopper",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 1,
            "section_name": "Section A",
            "batch_id": None,
            "student_count": 50,
            "course_id": 102,
            "course_code": "CS102",
            "course_type": "THEORY",
            "hour_type": "THEORY",
        },
    ]

    is_valid, violations, stats = verify_timetable_data(entries)
    assert is_valid is True
    assert len(violations) == 0
    assert stats["hard_constraint_status"] == "PASSED"


def test_faculty_clash_detected():
    # Dr. Alan Turing scheduled in two different rooms at the same time
    entries = [
        {
            "id": 1,
            "day": "MON",
            "start_time": "09:00",
            "end_time": "10:00",
            "faculty_id": 1,
            "faculty_name": "Dr. Alan Turing",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 1,
            "section_name": "Section A",
            "student_count": 50,
            "course_id": 101,
            "course_code": "CS101",
            "hour_type": "THEORY",
        },
        {
            "id": 2,
            "day": "MON",
            "start_time": "09:00",
            "end_time": "10:00",
            "faculty_id": 1,
            "faculty_name": "Dr. Alan Turing",
            "room_id": 2,
            "room_number": "CR-102",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 2,
            "section_name": "Section B",
            "student_count": 50,
            "course_id": 102,
            "course_code": "CS102",
            "hour_type": "THEORY",
        },
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is False
    assert any("[FACULTY_CLASH]" in v for v in violations)


def test_room_clash_detected():
    # Room CR-101 scheduled for two different courses at the same time
    entries = [
        {
            "id": 1,
            "day": "TUE",
            "start_time": "11:00",
            "end_time": "12:00",
            "faculty_id": 1,
            "faculty_name": "Dr. Alan Turing",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 1,
            "section_name": "Section A",
            "student_count": 40,
            "course_id": 101,
            "course_code": "CS101",
            "hour_type": "THEORY",
        },
        {
            "id": 2,
            "day": "TUE",
            "start_time": "11:00",
            "end_time": "12:00",
            "faculty_id": 2,
            "faculty_name": "Dr. Grace Hopper",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 60,
            "section_id": 2,
            "section_name": "Section B",
            "student_count": 40,
            "course_id": 102,
            "course_code": "CS102",
            "hour_type": "THEORY",
        },
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is False
    assert any("[ROOM_CLASH]" in v for v in violations)


def test_capacity_violation_detected():
    entries = [
        {
            "id": 1,
            "day": "WED",
            "start_time": "09:00",
            "end_time": "10:00",
            "faculty_id": 1,
            "faculty_name": "Dr. Alan Turing",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",
            "room_capacity": 30,  # Capacity 30
            "section_id": 1,
            "section_name": "Section A",
            "student_count": 55,  # Class size 55 > 30
            "course_id": 101,
            "course_code": "CS101",
            "hour_type": "THEORY",
        }
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is False
    assert any("[CAPACITY_VIOLATION]" in v for v in violations)


def test_consecutive_lab_blocks_valid():
    # 2-hour lab block: 14:00-15:00 and 15:00-16:00 in same LAB-101
    entries = [
        {
            "id": 1,
            "course_assignment_id": 10,
            "course_id": 501,
            "course_code": "CS501-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "THU",
            "start_time": "14:00",
            "end_time": "15:00",
            "room_id": 10,
            "room_number": "LAB-101",
            "room_type": "LAB",
            "room_capacity": 40,
            "faculty_id": 5,
            "batch_id": 1,
            "student_count": 20,
        },
        {
            "id": 2,
            "course_assignment_id": 10,
            "course_id": 501,
            "course_code": "CS501-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "THU",
            "start_time": "15:00",
            "end_time": "16:00",
            "room_id": 10,
            "room_number": "LAB-101",
            "room_type": "LAB",
            "room_capacity": 40,
            "faculty_id": 5,
            "batch_id": 1,
            "student_count": 20,
        },
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is True
    assert len(violations) == 0


def test_non_consecutive_lab_gap_detected():
    # Lab block split with a 1-hour gap: 14:00-15:00 and 16:00-17:00 (15:00-16:00 gap)
    entries = [
        {
            "id": 1,
            "course_assignment_id": 10,
            "course_id": 501,
            "course_code": "CS501-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "THU",
            "start_time": "14:00",
            "end_time": "15:00",
            "room_id": 10,
            "room_number": "LAB-101",
            "room_type": "LAB",
            "room_capacity": 40,
            "faculty_id": 5,
            "batch_id": 1,
            "student_count": 20,
        },
        {
            "id": 2,
            "course_assignment_id": 10,
            "course_id": 501,
            "course_code": "CS501-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "THU",
            "start_time": "16:00",
            "end_time": "17:00",
            "room_id": 10,
            "room_number": "LAB-101",
            "room_type": "LAB",
            "room_capacity": 40,
            "faculty_id": 5,
            "batch_id": 1,
            "student_count": 20,
        },
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is False
    assert any("[NON_CONSECUTIVE_LAB]" in v for v in violations)


def test_lab_in_classroom_detected():
    entries = [
        {
            "id": 1,
            "course_assignment_id": 10,
            "course_id": 501,
            "course_code": "CS501-LAB",
            "course_type": "LAB",
            "hour_type": "PRACTICAL",
            "day": "FRI",
            "start_time": "14:00",
            "end_time": "15:00",
            "room_id": 1,
            "room_number": "CR-101",
            "room_type": "CLASSROOM",  # Invalid facility type for a lab
            "room_capacity": 60,
            "faculty_id": 5,
            "batch_id": 1,
            "student_count": 20,
        }
    ]

    is_valid, violations, _ = verify_timetable_data(entries)
    assert is_valid is False
    assert any("[LAB_SUITABILITY_VIOLATION]" in v for v in violations)

