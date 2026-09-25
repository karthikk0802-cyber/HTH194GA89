# DAG validation from data: for each prerequisite edge A->B, compare average
# mastery of B between users who completed A and users who did not.
# Edges the data contradicts are flagged for review. Read-only.
# Run: python3 scripts/validate_dag.py
"""Check whether asserted prerequisites predict downstream mastery."""

import os
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from services.adaptive import build_competency_graph


def main():
    conn = sqlite3.connect("./onboardiq.db")
    try:
        rows = conn.execute(
            "SELECT user_id, topic_id, status, mastery_score FROM user_topic_states").fetchall()
    finally:
        conn.close()

    completed: dict = {}
    mastery: dict = {}
    for user_id, topic_id, status, score in rows:
        if status == "Completed":
            completed.setdefault(topic_id, set()).add(user_id)
        mastery.setdefault(topic_id, {})[user_id] = score or 0

    print(f"{'edge':40s} {'with_A':>8s} {'wout_A':>8s} {'delta':>7s}  verdict")
    flagged = 0
    for a, b in sorted(build_competency_graph().edges()):
        with_a = [s for u, s in mastery.get(b, {}).items() if u in completed.get(a, set())]
        wout_a = [s for u, s in mastery.get(b, {}).items() if u not in completed.get(a, set())]
        if not with_a or not wout_a:
            print(f"{a + ' -> ' + b:40s} {'n/a':>8s} {'n/a':>8s} {'n/a':>7s}  need more data")
            continue
        ma, mb = sum(with_a) / len(with_a), sum(wout_a) / len(wout_a)
        delta = ma - mb
        ok = delta >= 0
        flagged += 0 if ok else 1
        print(f"{a + ' -> ' + b:40s} {ma:8.1f} {mb:8.1f} {delta:+7.1f}  {'holds' if ok else 'CONTRADICTED'}")
    print(f"\n{flagged} edge(s) contradicted by data.")


if __name__ == "__main__":
    main()
