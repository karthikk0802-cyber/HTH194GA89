# Quarterly outcome export: joins users, diagnostic history, and mastery into
# one CSV for external analysis (probation ratings, ramp time live elsewhere).
# Read-only. Run: python3 scripts/outcome_export.py > outcome.csv
"""Correlate readiness-at-30-days with real outcomes to prove the platform works."""

import csv
import os
import sqlite3
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def main():
    auth = sqlite3.connect("./auth.db")
    app = sqlite3.connect("./onboardiq.db")
    try:
        users = {r[0]: r[1:] for r in auth.execute(
            "SELECT username, full_name, role, department, created_at FROM auth_users")}
        states = app.execute(
            "SELECT user_id, topic_id, status, difficulty, mastery_score,"
            " last_attempt_at FROM user_topic_states").fetchall()
        profiles = {r[0]: r[1:] for r in app.execute(
            "SELECT user_id, xp, level, streak_days FROM user_profiles")}
    finally:
        auth.close()
        app.close()

    by_user: dict = {}
    for user_id, topic_id, status, difficulty, mastery, attempted in states:
        d = by_user.setdefault(user_id, {"topics": 0, "expert": 0, "mastery_sum": 0,
                                         "completed": 0, "last_attempt": ""})
        d["topics"] += 1
        d["mastery_sum"] += mastery or 0
        if difficulty == "Expert":
            d["expert"] += 1
        if status == "Completed":
            d["completed"] += 1
        if attempted and attempted > d["last_attempt"]:
            d["last_attempt"] = attempted

    w = csv.writer(sys.stdout)
    w.writerow(["user_id", "full_name", "role", "department", "created_at",
                "topics", "completed", "expert", "avg_mastery", "xp", "level",
                "streak_days", "last_attempt"])
    for user_id, (name, role, dept, created) in sorted(users.items()):
        d = by_user.get(user_id, {"topics": 0, "expert": 0, "mastery_sum": 0,
                                  "completed": 0, "last_attempt": ""})
        xp, level, streak = profiles.get(user_id, (0, 1, 0))
        avg = round(d["mastery_sum"] / d["topics"], 1) if d["topics"] else 0
        w.writerow([user_id, name, role, dept, created, d["topics"], d["completed"],
                    d["expert"], avg, xp, level, streak, d["last_attempt"]])


if __name__ == "__main__":
    main()
