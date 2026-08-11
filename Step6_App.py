"""
Step 6: unified library application. Combines Person A's item/loan/fine/donation
features with Person B's people/event features into one menu over one shared
DB connection, per the assignment's "build your database application" requirement.
"""
import sqlite3

import Step6_PersonA_App as person_a
import Step6_PersonB_App as person_b


def main():
    conn = person_b.connect()
    person_a.sync_overdue_loans(conn)
    cur = conn.cursor()
    menu = """
1) Find an item
2) Borrow an item
3) Return an item
4) Donate an item
5) Find an event
6) Register for an event
7) Volunteer
8) Ask a librarian
9) Exit
"""
    actions = {
        "1": lambda: person_a.find_item(cur),
        "2": lambda: person_a.borrow_item(conn, cur),
        "3": lambda: person_a.return_item(conn, cur),
        "4": lambda: person_a.donate_item(conn, cur),
        "5": lambda: person_b.find_event(cur),
        "6": lambda: person_b.register_event(conn, cur),
        "7": lambda: person_b.volunteer(conn, cur),
        "8": lambda: person_b.ask_librarian(cur),
    }
    while True:
        print(menu)
        try:
            choice = input("Choose an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if choice == "9":
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
