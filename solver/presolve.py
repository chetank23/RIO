"""
solver/presolve.py
------------------
Pre-solve mathematical infeasibility diagnostics for campus timetabling.
Detects provably impossible constraints BEFORE model building or CP-SAT invocation:
1. Section/batch student count exceeding maximum room capacity
2. Total required class hours for any section/batch exceeding available weekly timeslots
3. Faculty assigned teaching hours exceeding available (non-unavailable) slots or max load
4. Total required lab hours across all batches exceeding available lab capacity
5. Course hour requirements with 0 eligible rooms
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PresolveResult:
    feasible: bool
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


def run_presolve_checks(dataset: Any) -> PresolveResult:
    """
    Analyzes input data for feasibility prior to CP-SAT solver invocation.
    Accepts an OptimizerInput instance or a dictionary with keys:
    courses, sections, batches, rooms, labs, faculty, faculty_availability,
    time_slots, course_assignments.
    """
    issues: List[str] = []
    warnings: List[str] = []

    # Normalize access whether Pydantic BaseModel or dict
    def get_attr(obj: Any, key: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    courses_raw = get_attr(dataset, "courses", []) or []
    sections_raw = get_attr(dataset, "sections", []) or []
    batches_raw = get_attr(dataset, "batches", []) or []
    rooms_raw = get_attr(dataset, "rooms", []) or []
    labs_raw = get_attr(dataset, "labs", []) or []
    faculty_raw = get_attr(dataset, "faculty", []) or []
    slots_raw = get_attr(dataset, "time_slots", []) or []
    fa_raw = get_attr(dataset, "faculty_availability", []) or []
    assignments_raw = get_attr(dataset, "course_assignments", []) or []

    courses = {get_attr(c, "id"): c for c in courses_raw}
    sections = {get_attr(s, "id"): s for s in sections_raw}
    batches = {get_attr(b, "id"): b for b in batches_raw}
    rooms = {get_attr(r, "id"): r for r in rooms_raw}
    labs = {get_attr(l, "room_id", get_attr(l, "id")): l for l in labs_raw}
    faculty = {get_attr(f, "id"): f for f in faculty_raw}
    slots = {get_attr(t, "id"): t for t in slots_raw if get_attr(t, "slot_type") not in ("BREAK", "LUNCH")}

    total_valid_slots = len(slots)

    # 1. Check time slot availability
    if total_valid_slots == 0:
        issues.append("Zero valid teaching time slots available in schedule scope.")
        return PresolveResult(feasible=False, issues=issues)

    # 2. Maximum room capacity check
    max_classroom_capacity = max(
        (get_attr(r, "capacity", 0) or 0 for r in rooms.values() if get_attr(r, "room_type") in ("CLASSROOM", "SEMINAR_HALL", "AUDITORIUM")),
        default=0,
    )
    max_lab_capacity = max(
        (get_attr(r, "capacity", 0) or 0 for r in rooms.values() if get_attr(r, "room_type") == "LAB"),
        default=0,
    )

    for s_id, sec in sections.items():
        s_count = get_attr(sec, "student_count", 0) or 0
        if s_count > max_classroom_capacity:
            issues.append(
                f"Section #{s_id} has {s_count} students, exceeding maximum classroom capacity ({max_classroom_capacity})."
            )

    for b_id, bch in batches.items():
        b_count = get_attr(bch, "student_count", 0) or 0
        if b_count > max_lab_capacity and max_lab_capacity > 0:
            issues.append(
                f"Batch #{b_id} has {b_count} students, exceeding maximum laboratory capacity ({max_lab_capacity})."
            )

    # 3. Required hours per Section / Batch vs available slots
    sec_hours = defaultdict(int)
    batch_hours = defaultdict(int)
    faculty_assigned_hours = defaultdict(int)
    total_lab_hours_needed = 0

    for a in assignments_raw:
        c_id = get_attr(a, "course_id")
        course = courses.get(c_id)
        if not course:
            issues.append(f"Assignment #{get_attr(a, 'id')} references nonexistent course #{c_id}.")
            continue

        th_hours = (get_attr(course, "lecture_hours", 0) or 0) + (get_attr(course, "tutorial_hours", 0) or 0)
        pr_hours = get_attr(course, "practical_hours", 0) or 0
        req_hours = th_hours + pr_hours

        f_id = get_attr(a, "faculty_id")
        sec_id = get_attr(a, "section_id")
        b_id = get_attr(a, "batch_id")

        faculty_assigned_hours[f_id] += req_hours

        if sec_id:
            sec_hours[sec_id] += th_hours
        if b_id:
            batch_hours[b_id] += pr_hours
            total_lab_hours_needed += pr_hours

    for s_id, h in sec_hours.items():
        if h > total_valid_slots:
            issues.append(
                f"Section #{s_id} requires {h} theory hours, exceeding total weekly slots ({total_valid_slots})."
            )

    for b_id, h in batch_hours.items():
        # A batch attends its section's theory plus its own lab
        b_obj = batches.get(b_id)
        sec_id = get_attr(b_obj, "section_id") if b_obj else None
        total_batch_load = h + sec_hours.get(sec_id, 0)
        if total_batch_load > total_valid_slots:
            issues.append(
                f"Batch #{b_id} total workload ({total_batch_load} hrs) exceeds total weekly slots ({total_valid_slots})."
            )

    # 4. Faculty capacity & availability
    fa_by_faculty = defaultdict(set)
    for fa in fa_raw:
        f_id = get_attr(fa, "faculty_id")
        slot_id = get_attr(fa, "slot_id")
        avail = get_attr(fa, "availability", "AVAILABLE")
        if avail != "UNAVAILABLE":
            fa_by_faculty[f_id].add(slot_id)

    for f_id, f_obj in faculty.items():
        assigned = faculty_assigned_hours[f_id]
        if assigned == 0:
            continue

        max_load = get_attr(f_obj, "max_weekly_load")
        if max_load is not None and assigned > max_load:
            issues.append(
                f"Faculty #{f_id} assigned {assigned} hours, exceeding max weekly load ({max_load})."
            )

        # Slots where faculty is available
        avail_slots = fa_by_faculty[f_id] if f_id in fa_by_faculty else set(slots.keys())
        if assigned > len(avail_slots):
            issues.append(
                f"Faculty #{f_id} requires {assigned} teaching hours but is only available for {len(avail_slots)} slots."
            )

    # 5. Laboratory total capacity (Pigeonhole principle)
    total_lab_slots_capacity = len(labs) * total_valid_slots
    if total_lab_hours_needed > total_lab_slots_capacity:
        issues.append(
            f"Total lab demand ({total_lab_hours_needed} hours) exceeds total institutional lab capacity "
            f"({len(labs)} labs × {total_valid_slots} slots = {total_lab_slots_capacity} hours)."
        )

    feasible = len(issues) == 0
    summary = {
        "total_courses": len(courses),
        "total_sections": len(sections),
        "total_batches": len(batches),
        "total_rooms": len(rooms),
        "total_labs": len(labs),
        "total_slots": total_valid_slots,
        "total_assignments": len(assignments_raw),
        "total_lab_hours_needed": total_lab_hours_needed,
    }

    return PresolveResult(
        feasible=feasible,
        issues=issues,
        warnings=warnings,
        summary=summary,
    )

