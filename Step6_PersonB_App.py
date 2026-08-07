"""
Step 6 - Person B's app features: find an event, register for an event, volunteer,
ask a librarian. Connects to library.db (built by build_db.py from both Step4/Step5 halves).
All SQL uses parameterized queries (never string-formats user input into SQL).
Every menu action commits on success and rolls back on any sqlite3.Error.
"""
import os
import sqlite3
from datetime import date

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def next_person_id(cur):
    # Take the numeric max, not the textual one: 'P999' sorts after 'P1000' as text,
    # which would regenerate an existing ID once past P999.
    cur.execute("SELECT MAX(CAST(SUBSTR(personID, 2) AS INTEGER)) FROM Person")
    n = (cur.fetchone()[0] or 0) + 1
    return f"P{n:03d}"


def find_event(cur):
    keyword = input("Search events by title/type/description (blank lists all): ").strip()
    like = f"%{keyword}%"
    cur.execute(
        """
        SELECT e.eventID, e.title, e.eventType, e.eventDate,
               e.startTime || '-' || e.endTime AS timeSlot,
               r.name AS roomName,
               r.capacity - COUNT(DISTINCT a.personID) AS spotsLeft,
               COALESCE(GROUP_CONCAT(DISTINCT rf.groupName), '-') AS audiences
        FROM Event e
        JOIN Room r ON r.roomID = e.roomID
        LEFT JOIN Attends a ON a.eventID = e.eventID
        LEFT JOIN RecommendedFor rf ON rf.eventID = e.eventID
        WHERE e.title LIKE ? OR e.eventType LIKE ? OR COALESCE(e.description, '') LIKE ?
        GROUP BY e.eventID
        ORDER BY e.eventDate, e.startTime, e.eventID
        """,
        (like, like, like),
    )
    rows = cur.fetchall()
    if not rows:
        print("No events found.\n")
        return
    print(f"\n{'eventID':<9}{'title':<34}{'type':<15}{'date':<12}{'time':<14}{'room':<18}{'spots':<7}{'audience':<20}")
    for eventID, title, eventType, eventDate, timeSlot, roomName, spotsLeft, audiences in rows:
        print(f"{eventID:<9}{title:<34}{eventType:<15}{eventDate:<12}{timeSlot:<14}{roomName:<18}{spotsLeft:<7}{audiences:<20}")

    eventID = input("\nEvent ID for details (blank to skip): ").strip()
    if not eventID:
        print()
        return
    cur.execute(
        """
        SELECT e.title, COALESCE(e.description, '(no description)'), e.eventDate,
               e.startTime, e.endTime, r.name
        FROM Event e
        JOIN Room r ON r.roomID = e.roomID
        WHERE e.eventID = ?
        ORDER BY e.eventID
        """,
        (eventID,),
    )
    row = cur.fetchone()
    if not row:
        print(f"No event with ID {eventID}.\n")
        return
    title, description, eventDate, startTime, endTime, roomName = row
    print(f"\n{title}\n  {description}\n  {eventDate} {startTime}-{endTime} in the {roomName}\n")


def register_event(conn, cur):
    personID = input("Your person ID: ").strip()
    cur.execute("SELECT name FROM Person WHERE personID = ? ORDER BY personID", (personID,))
    person = cur.fetchone()
    if not person:
        print(f"No person with ID {personID}. (New volunteers can sign up from the main menu.)\n")
        return

    eventID = input("Event ID to register for: ").strip()
    cur.execute("SELECT title, eventDate FROM Event WHERE eventID = ? ORDER BY eventID", (eventID,))
    event = cur.fetchone()
    if not event:
        print(f"No event with ID {eventID}.\n")
        return

    cur.execute(
        "SELECT registrationDate FROM Attends WHERE personID = ? AND eventID = ? ORDER BY personID",
        (personID, eventID),
    )
    existing = cur.fetchone()
    if existing:
        print(f"{person[0]} is already registered for {eventID} (since {existing[0]}).\n")
        return

    cur.execute(
        "INSERT INTO Attends (personID, eventID, registrationDate) VALUES (?, ?, ?)",
        (personID, eventID, date.today().isoformat()),
    )
    print(f"Registered {person[0]} for \"{event[0]}\" on {event[1]}. See you there!\n")


def volunteer(conn, cur):
    personID = input("Your person ID (blank if you are new to the library): ").strip()
    if personID:
        cur.execute("SELECT name FROM Person WHERE personID = ? ORDER BY personID", (personID,))
        person = cur.fetchone()
        if not person:
            print(f"No person with ID {personID}. Leave the ID blank to sign up as new.\n")
            return
        name = person[0]
    else:
        name = input("  Your name: ").strip()
        email = input("  Your email: ").strip()
        phone = input("  Your phone (optional): ").strip() or None
        address = input("  Your address (optional): ").strip() or None
        if not name or not email:
            print("Name and email are required to sign up.\n")
            return
        personID = next_person_id(cur)
        cur.execute(
            "INSERT INTO Person (personID, name, email, phone, address) VALUES (?, ?, ?, ?, ?)",
            (personID, name, email, phone, address),
        )
        print(f"Welcome, {name}! Your person ID is {personID}.")

    cur.execute(
        "SELECT startDate, hoursLogged FROM Volunteer WHERE personID = ? ORDER BY personID",
        (personID,),
    )
    existing = cur.fetchone()
    if existing:
        print(f"{name} has been a volunteer since {existing[0]} ({existing[1]} hours logged). Thank you!\n")
        return

    cur.execute(
        "INSERT INTO Volunteer (personID, startDate, hoursLogged) VALUES (?, ?, 0)",
        (personID, date.today().isoformat()),
    )
    print(f"{name} is now signed up as a volunteer. Thank you!\n")


def ask_librarian(cur):
    question = input("What would you like to ask? ").strip() or "(no question entered)"
    cur.execute(
        """
        SELECT p.name, s.role, p.email, COALESCE(p.phone, 'no phone on file')
        FROM Staff s
        JOIN Person p ON p.personID = s.personID
        WHERE s.role LIKE '%Librarian%'
        ORDER BY s.hireDate, s.personID
        """
    )
    rows = cur.fetchall()
    if not rows:
        print("No librarians are on staff right now. Please visit the front desk.\n")
        return
    print(f"\nOur librarians would be happy to help with: \"{question}\"")
    print(f"{'name':<20}{'role':<22}{'email':<32}{'phone':<16}")
    for name, role, email, phone in rows:
        print(f"{name:<20}{role:<22}{email:<32}{phone:<16}")
    print(f"\nFor the quickest answer, email {rows[0][0]} ({rows[0][2]}) or visit the front desk.\n")


def main():
    conn = connect()
    cur = conn.cursor()
    menu = """
1) Find an event
2) Register for an event
3) Volunteer
4) Ask a librarian
5) Exit
"""
    actions = {
        "1": lambda: find_event(cur),
        "2": lambda: register_event(conn, cur),
        "3": lambda: volunteer(conn, cur),
        "4": lambda: ask_librarian(cur),
    }
    while True:
        print(menu)
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if choice == "5":
            break
        action = actions.get(choice)
        if not action:
            print("Invalid option.\n")
            continue
        try:
            action()
            conn.commit()
        except sqlite3.Error as e:
            conn.rollback()
            print(f"Database error: {e}\nNothing was changed.\n")
        except (EOFError, KeyboardInterrupt):
            conn.rollback()
            print("\nCancelled; nothing was changed.\n")
    conn.close()


if __name__ == "__main__":
    main()
