import csv
import json
import sys
from pathlib import Path

LABEL_COLS = [
    "error_detection",      # hit / miss / false_positive
    "math_guidance",        # correct / partial / incorrect
    "premature_answer",     # yes / no
    "state_regression",     # yes / no
    "meta_timing",          # ok / early / late / missing
    "notes",
]

def extract_to_csv(jsonl_path: str, out_path: str | None = None):
    src = Path(jsonl_path)
    out = Path(out_path) if out_path else src.with_suffix(".csv")

    rows = []
    with src.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            r = json.loads(line)
            v = r.get("verification") or {}
            rows.append({
                "turn": i,
                "trajectory_id": r.get("trajectory_id"),
                "ablation_mode": r.get("ablation_mode"),
                "student_input": r.get("student_input"),
                "final_response": r.get("final_response"),
                "problem_solved": r.get("problem_solved"),
                "reflection_count": r.get("reflection_count"),
                "next_agent": r.get("next_agent"),
                "emotion": r.get("emotion"),
                "verif_parseable": v.get("parseable"),
                "verif_error_type": v.get("error_type"),
                "verif_problem_solved": v.get("problem_solved"),
                "verif_answer": v.get("verified_answer"),
                "orchestrator_instruction": r.get("orchestrator_instruction"),
                **{c: "" for c in LABEL_COLS},
            })

    fieldnames = list(rows[0].keys()) if rows else []
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} turns → {out}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python eval/extract_turns.py path/to/file.jsonl")
        sys.exit(1)
    extract_to_csv(sys.argv[1])