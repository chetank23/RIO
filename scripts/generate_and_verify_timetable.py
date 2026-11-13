"""
scripts/generate_and_verify_timetable.py
----------------------------------------
End-to-end integration script that:
1. Loads academic data from SQLite data/campus.db
2. Runs pre-solve feasibility checks (solver.presolve)
3. Solves timetable using Google OR-Tools CP-SAT (solver.TimetableSolver)
4. Exports generated schedule to data/generated_timetable.json
5. Verifies all 5 hard constraints using standalone verifier (solver.verify_timetable)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.config import SessionLocal
from backend.models.academic import AcademicYear, Semester, Department
from backend.schemas.timetable_generation import GenerationScope
from backend.services.timetable_input_loader import validate_and_load_input
from solver import TimetableSolver, run_presolve_checks, validate_timetable, calculate_timetable_score
from solver.verify_timetable import verify_timetable_data


def run_pipeline():
    print("=" * 70)
    print(" RIO END-TO-END TIMETABLE SOLVER & VERIFIER PIPELINE")
    print("=" * 70)

    # 1. Connect to DB
    print("[1/5] Connecting to SQLite database...")
    db = SessionLocal()

    try:
        ay = db.query(AcademicYear).first()
        sem = db.query(Semester).first()
        dept = db.query(Department).first()

        if not ay or not sem or not dept:
            print("[ERROR] Database lacks core academic metadata. Run scripts/seed_sqlite.py first.")
            sys.exit(1)

        print(f"      Academic Year: {ay.name} (ID: {ay.id})")
        print(f"      Semester:      Semester {sem.semester_number} (ID: {sem.id})")
        print(f"      Department:    {dept.name} (ID: {dept.id})")

        scope = GenerationScope(
            academic_year_id=ay.id,
            semester_id=sem.id,
            department_id=dept.id,
        )

        # 2. Load input
        print("[2/5] Loading optimization dataset...")
        opt_input = validate_and_load_input(db, scope)
        print(f"      Loaded: {len(opt_input.sections)} sections, {len(opt_input.batches)} batches, "
              f"{len(opt_input.courses)} courses, {len(opt_input.faculty)} faculty, "
              f"{len(opt_input.rooms)} rooms, {len(opt_input.time_slots)} slots, "
              f"{len(opt_input.course_assignments)} assignments.")

        # 3. Presolve checks
        print("[3/5] Running pre-solve mathematical infeasibility checks...")
        presolve_res = run_presolve_checks(opt_input)
        if not presolve_res.feasible:
            print("[ERROR] Pre-solve checks failed with issues:")
            for issue in presolve_res.issues:
                print(f"      ❌ {issue}")
            sys.exit(1)
        print("      ✅ Pre-solve checks passed: Dataset is mathematically solvable.")

        # 4. Run CP-SAT solver
        print("[4/5] Invoking Google OR-Tools CP-SAT Timetable Solver...")
        solver = TimetableSolver(opt_input=opt_input, time_limit=60, strategy="BALANCED")
        solver.build_model()
        result = solver.solve()

        if not result.feasible:
            print("[ERROR] Solver failed to find a feasible solution.")
            if result.diagnostics:
                print(f"      Diagnostics: {result.diagnostics}")
            sys.exit(1)

        print(f"      ✅ Feasible timetable produced! Total scheduled entries: {len(result.entries)}")
        print(f"      Solve time: {result.solve_time_seconds:.2f} seconds | Status: {result.status}")

        # Compute internal score
        val_res = validate_timetable(result.entries, opt_input)
        score_dict = calculate_timetable_score(val_res, result.entries, opt_input)
        print(f"      Solver Quality Score: {score_dict.get('total_score', 'N/A')} / 100")

        # 5. Export JSON for independent verification
        output_path = BASE_DIR / "data" / "generated_timetable.json"
        
        # Build export records with metadata
        rooms_by_id = {r.id: r for r in opt_input.rooms}
        slots_by_id = {s.id: s for s in opt_input.time_slots}
        courses_by_id = {c.id: c for c in opt_input.courses}
        faculty_by_id = {f.id: f for f in opt_input.faculty}
        sections_by_id = {s.id: s for s in opt_input.sections}
        batches_by_id = {b.id: b for b in opt_input.batches}
        assignments_by_id = {a.id: a for a in opt_input.course_assignments}

        export_entries = []
        for idx, entry in enumerate(result.entries):
            a = assignments_by_id.get(entry.course_assignment_id)
            c = courses_by_id.get(a.course_id) if a else None
            r = rooms_by_id.get(entry.room_id)
            s = slots_by_id.get(entry.slot_id)
            f = faculty_by_id.get(a.faculty_id) if a else None
            sec = sections_by_id.get(a.section_id) if (a and a.section_id) else None
            batch = batches_by_id.get(a.batch_id) if (a and a.batch_id) else None

            export_entries.append({
                "id": idx + 1,
                "course_assignment_id": entry.course_assignment_id,
                "course_id": c.id if c else None,
                "course_code": getattr(c, "code", f"CRS-{c.id}") if c else f"CRS-{entry.course_assignment_id}",
                "course_type": getattr(c, "course_type", "THEORY") if c else "THEORY",
                "hour_type": entry.hour_type,
                "day": s.day if s else "MON",
                "start_time": s.start_time.strftime("%H:%M") if (s and s.start_time) else "09:00",
                "end_time": s.end_time.strftime("%H:%M") if (s and s.end_time) else "10:00",
                "room_id": entry.room_id,
                "room_number": getattr(r, "number", f"R-{entry.room_id}") if r else f"R-{entry.room_id}",
                "room_type": getattr(r, "room_type", "CLASSROOM") if r else "CLASSROOM",
                "room_capacity": getattr(r, "capacity", 60) if r else 60,
                "faculty_id": f.id if f else None,
                "faculty_name": f"Faculty {f.id}" if f else "Unknown",
                "section_id": sec.id if sec else None,
                "section_name": f"Section {sec.id}" if sec else "None",
                "batch_id": batch.id if batch else None,
                "batch_name": f"Batch {batch.id}" if batch else "None",
                "student_count": (batch.student_count if batch else (sec.student_count if sec else 30)),
            })

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({"entries": export_entries}, f, indent=2)

        print(f"[5/5] Exported schedule to {output_path}")
        print("      Running Independent Zero-Dependency Verifier CLI...")

        is_valid, violations, stats = verify_timetable_data(export_entries)
        print("-" * 70)
        print(f"      Verification Status: {'PASSED' if is_valid else 'FAILED'}")
        print(f"      Hard Constraint Violations: {len(violations)}")
        if not is_valid:
            for v in violations:
                print(f"      ❌ {v}")
            sys.exit(1)
        else:
            print("      ✅ Faculty Double-Booking: 0 clashes")
            print("      ✅ Room Double-Booking:    0 clashes")
            print("      ✅ Cohort Double-Booking:  0 clashes")
            print("      ✅ Room Capacity Limits:   Satisfied")
            print("      ✅ Consecutive Lab Blocks: Satisfied (2-3 period contiguous blocks in Labs)")
            print("=" * 70)
            print("PIPELINE RESULT: 100% VERIFIED AND COMPLIANT")
            print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_pipeline()
