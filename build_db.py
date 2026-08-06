"""
Builds library.db from scratch out of both halves' Step 4/5 SQL files, in dependency
order: Person B's schema loads first because Person A's Item/Loan/AcquisitionCandidate
reference Person(personID) once their FKs are enabled, and Person B's data loads before
Person A's for the same reason. Verifies the result with PRAGMA foreign_key_check and
PRAGMA integrity_check, and exits non-zero if either fails.
"""
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(HERE, "library.db")
SQL_FILES = [
    "Step4_PersonB_Schema.sql",
    "Step4_PersonA_Schema.sql",
    "Step5_PersonB_Data.sql",
    "Step5_PersonA_Data.sql",
]


def main():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        for fname in SQL_FILES:
            with open(os.path.join(HERE, fname)) as f:
                conn.executescript(f.read())
            print(f"loaded: {fname}")
        conn.commit()
        fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
        integrity = conn.execute("PRAGMA integrity_check").fetchall()
    finally:
        conn.close()

    ok = True
    if fk_rows:
        ok = False
        print("foreign_key_check FAILED:")
        for row in fk_rows:
            print("   ", row)
    else:
        print("foreign_key_check: ok")
    if integrity == [("ok",)]:
        print("integrity_check: ok")
    else:
        ok = False
        print(f"integrity_check FAILED: {integrity}")

    if not ok:
        sys.exit(1)
    print(f"built: {DB_FILE}")


if __name__ == "__main__":
    main()
