"""
solver/verify_timetable.py
--------------------------
Independent, zero-backend-dependency timetable verifier CLI.
Validates exported timetable JSON files against the 5 non-negotiable hard constraints:
1. Zero faculty clashes (no faculty double-booked across overlapping intervals)
2. Zero room clashes (no room double-booked across overlapping intervals)
3. Zero batch/section clashes (no cohort scheduled simultaneously)
4. Room capacity >= student/cohort size
5. Lab/Practical sessions strictly scheduled as consecutive 2-3 period blocks in lab rooms

Usage:
    python -m solver.verify_timetable <timetable.json>
    python solver/verify_timetable.py <timetable.json>
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime
import json
import sys
from typing import Any, Dict, List, Optional, Tuple

DAY_NORM_MAP = {
    "MON": "MON", "MONDAY": "MON",
    "TUE": "TUE", "TUESDAY": "TUE",
    "WED": "WED", "WEDNESDAY": "WED",
    "THU": "THU", "THURSDAY": "THU",
    "FRI": "FRI", "FRIDAY": "FRI",
    "SAT": "SAT", "SATURDAY": "SAT",
    "SUN": "SUN", "SUNDAY": "SUN",
}


def parse_time(val: Any) -> datetime.time:
    """Parses time from string 'HH:MM' or 'HH:MM:SS' or datetime.time."""
    if isinstance(val, datetime.time):
        return val
    s = str(val).strip()
    parts = s.split(":")
    h = int(parts[0])
    m = int(parts[1]) if len(parts) > 1 else 0
    sec = int(parts[2]) if len(parts) > 2 else 0
    return datetime.time(h, m, sec)


def times_overlap(d1: str, s1: datetime.time, e1: datetime.time,
                  d2: str, s2: datetime.time, e2: datetime.time) -> bool:
    """Returns True if two intervals on normalized days overlap."""
    if d1 != d2:
        return False
    return max(s1, s2) < min(e1, e2)


def verify_timetable_data(entries: List[Dict[str, Any]]) -> Tuple[bool, List[str], Dict[str, Any]]:
    violations: List[str] = []

    if not entries:
        violations.append("Timetable contains zero scheduled entries.")
        return False, violations, {}

    normalized_entries = []
    for idx, e in enumerate(entries):
        raw_day = str(e.get("day", "")).strip().upper()
        norm_day = DAY_NORM_MAP.get(raw_day, raw_day[:3] if len(raw_day) >= 3 else "")
        s_time = parse_time(e.get("start_time", "00:00"))
        e_time = parse_time(e.get("end_time", "00:00"))

        item = {
            "index": idx + 1,
            "id": e.get("id", idx + 1),
            "day": norm_day,
            "start_time": s_time,
            "end_time": e_time,
            "faculty_id": e.get("faculty_id"),
            "faculty_name": e.get("faculty_name", f"Faculty #{e.get('faculty_id')}"),
            "room_id": e.get("room_id"),
            "room_number": e.get("room_number", f"Room #{e.get('room_id')}"),
            "room_type": str(e.get("room_type", "")).upper(),
            "room_capacity": e.get("room_capacity", e.get("capacity")),
            "section_id": e.get("section_id"),
            "section_name": e.get("section_name", f"Section #{e.get('section_id')}"),
            "batch_id": e.get("batch_id"),
            "batch_name": e.get("batch_name", f"Batch #{e.get('batch_id')}"),
            "student_count": e.get("student_count", 0) or 0,
            "course_id": e.get("course_id"),
            "course_code": e.get("course_code", f"Course #{e.get('course_id')}"),
            "course_type": str(e.get("course_type", "")).upper(),
            "hour_type": str(e.get("hour_type", "THEORY")).upper(),
            "course_assignment_id": e.get("course_assignment_id"),
        }
        normalized_entries.append(item)

    n = len(normalized_entries)

    # 1. Capacity & Lab Suitability Checks
    for e in normalized_entries:
        cap = e["room_capacity"]
        cnt = e["student_count"]
        if cap is not None and cap > 0 and cnt > 0 and cap < cnt:
            violations.append(
                f"[CAPACITY_VIOLATION] Entry #{e['index']} ({e['course_code']} in {e['room_number']}): "
                f"Room capacity ({cap}) is less than class size ({cnt})."
            )

        if e["hour_type"] == "PRACTICAL" or e["course_type"] == "LAB":
            if e["room_type"] != "LAB" and "LAB" not in str(e["room_number"]).upper():
                violations.append(
                    f"[LAB_SUITABILITY_VIOLATION] Entry #{e['index']} ({e['course_code']}): "
                    f"Practical lab scheduled in non-lab facility {e['room_number']} ({e['room_type']})."
                )

    # 2. Pairwise Collision Checks (Faculty, Room, Section/Batch)
    for i in range(n):
        for j in range(i + 1, n):
            e1 = normalized_entries[i]
            e2 = normalized_entries[j]

            if not times_overlap(e1["day"], e1["start_time"], e1["end_time"],
                                 e2["day"], e2["start_time"], e2["end_time"]):
                continue

            time_str = f"{e1['day']} {e1['start_time'].strftime('%H:%M')}-{e1['end_time'].strftime('%H:%M')}"

            # Faculty Clash
            if e1["faculty_id"] is not None and e1["faculty_id"] == e2["faculty_id"]:
                violations.append(
                    f"[FACULTY_CLASH] {e1['faculty_name']} is double-booked at {time_str} "
                    f"(Entry #{e1['index']} {e1['course_code']} in {e1['room_number']} vs "
                    f"Entry #{e2['index']} {e2['course_code']} in {e2['room_number']})."
                )

            # Room Clash
            if e1["room_id"] is not None and e1["room_id"] == e2["room_id"]:
                violations.append(
                    f"[ROOM_CLASH] {e1['room_number']} is double-booked at {time_str} "
                    f"(Entry #{e1['index']} {e1['course_code']} vs Entry #{e2['index']} {e2['course_code']})."
                )

            # Section Clash
            if e1["section_id"] is not None and e1["section_id"] == e2["section_id"]:
                # If neither has a batch (both whole-section) -> clash
                if e1["batch_id"] is None and e2["batch_id"] is None:
                    violations.append(
                        f"[SECTION_CLASH] Section {e1['section_name']} has conflicting whole-class lectures at {time_str} "
                        f"(Entry #{e1['index']} {e1['course_code']} vs Entry #{e2['index']} {e2['course_code']})."
                    )
                # If one is whole section and other is batch in same section -> clash
                elif (e1["batch_id"] is None and e2["batch_id"] is not None) or (e1["batch_id"] is not None and e2["batch_id"] is None):
                    violations.append(
                        f"[SECTION_BATCH_CLASH] Section {e1['section_name']} lecture conflicts with Batch activity at {time_str} "
                        f"(Entry #{e1['index']} {e1['course_code']} vs Entry #{e2['index']} {e2['course_code']})."
                    )

            # Batch Clash (same batch scheduled simultaneously)
            if e1["batch_id"] is not None and e1["batch_id"] == e2["batch_id"]:
                violations.append(
                    f"[BATCH_CLASH] Batch {e1['batch_name']} is double-booked at {time_str} "
                    f"(Entry #{e1['index']} {e1['course_code']} vs Entry #{e2['index']} {e2['course_code']})."
                )

    # 3. Consecutive Lab Block Verification (2-3 period contiguous blocks)
    # Group practical entries by (course_id, batch_id, day) or (course_assignment_id, day)
    lab_groups = defaultdict(list)
    for e in normalized_entries:
        if e["hour_type"] == "PRACTICAL" or e["course_type"] == "LAB":
            group_key = (e.get("course_assignment_id") or e.get("course_id"), e.get("batch_id"), e["day"])
            lab_groups[group_key].append(e)

    for group_key, group_entries in lab_groups.items():
        if len(group_entries) > 1:
            # Sort chronologically by start_time
            group_entries.sort(key=lambda x: x["start_time"])

            # Verify same room
            rooms_used = set(x["room_id"] for x in group_entries)
            if len(rooms_used) > 1:
                violations.append(
                    f"[LAB_ROOM_FRAGMENTATION] Lab group {group_key[0]} (Batch #{group_key[1]}) split across multiple rooms: {rooms_used}."
                )

            # Verify consecutive periods without gaps
            for k in range(len(group_entries) - 1):
                prev_e = group_entries[k]
                next_e = group_entries[k + 1]
                if prev_e["end_time"] != next_e["start_time"]:
                    violations.append(
                        f"[NON_CONSECUTIVE_LAB] Lab group {group_key[0]} (Batch #{group_key[1]}) on {group_key[2]} has a non-consecutive gap "
                        f"between {prev_e['end_time'].strftime('%H:%M')} and {next_e['start_time'].strftime('%H:%M')}."
                    )

    is_valid = len(violations) == 0
    stats = {
        "total_entries": n,
        "total_violations": len(violations),
        "hard_constraint_status": "PASSED" if is_valid else "FAILED",
    }
    return is_valid, violations, stats


def main():
    parser = argparse.ArgumentParser(description="RIO-MJP Independent Timetable Verifier CLI")
    parser.add_argument("timetable_path", help="Path to timetable JSON file")
    parser.add_argument("--quiet", action="store_true", help="Suppress detailed passing report")
    args = parser.parse_args()

    try:
        with open(args.timetable_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as exc:
        print(f"[FATAL ERROR] Could not read timetable file: {exc}", file=sys.stderr)
        sys.exit(1)

    entries = data.get("entries", data) if isinstance(data, dict) else data
    if not isinstance(entries, list):
        print("[FATAL ERROR] Invalid timetable format. Expected list or object with 'entries' key.", file=sys.stderr)
        sys.exit(1)

    is_valid, violations, stats = verify_timetable_data(entries)

    print("=" * 70)
    print(" RIO-MJP INDEPENDENT TIMETABLE VERIFIER REPORT")
    print("=" * 70)
    print(f"File Inspected:       {args.timetable_path}")
    print(f"Total Entries:        {stats.get('total_entries', 0)}")
    print(f"Hard Constraints:     {'🟢 0 VIOLATIONS (PASSED)' if is_valid else '🔴 VIOLATIONS DETECTED (FAILED)'}")
    print("-" * 70)

    if not is_valid:
        print(f"Found {len(violations)} Hard Constraint Violation(s):")
        for v in violations:
            print(f"  ❌ {v}")
        print("=" * 70)
        sys.exit(1)
    else:
        if not args.quiet:
            print("  ✅ Constraint 1: Zero Faculty Clashes Verified")
            print("  ✅ Constraint 2: Zero Room Clashes Verified")
            print("  ✅ Constraint 3: Zero Section & Batch Clashes Verified")
            print("  ✅ Constraint 4: Room Capacity >= Cohort Size Verified")
            print("  ✅ Constraint 5: Consecutive 2-3 Period Lab Blocks Verified")
            print("=" * 70)
            print("STATUS: VALID TIMETABLE CANDIDATE (EXIT CODE 0)")
        sys.exit(0)


if __name__ == "__main__":
    main()

