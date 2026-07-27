"""
Step 6 - Person A's app features: find an item, borrow an item, return an item,
donate an item. Connects to library.db (built from Step4 schema + Step5 data).
All SQL uses parameterized queries (never string-formats user input into SQL).
"""
import sqlite3
from datetime import date

DB_FILE = "library.db"
LOAN_PERIOD_DAYS = 14
FINE_RATE_PER_DAY = 0.50

ITEM_TYPES = {
    "1": ("PrintBook", ["ISBN", "shelfLocation"]),
    "2": ("OnlineBook", ["ISBN", "fileFormat", "accessURL"]),
    "3": ("Magazine", ["issueNumber", "publicationDate", "publisher"]),
    "4": ("Journal", ["volume", "issueNumber", "subjectArea"]),
    "5": ("Recording", ["artist", "format", "duration"]),
}


def connect():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def next_item_id(cur):
    cur.execute("SELECT itemID FROM Item ORDER BY itemID DESC LIMIT 1")
    row = cur.fetchone()
    n = int(row[0][2:]) + 1 if row else 1
    return f"IT{n:03d}"


def find_item(cur):
    keyword = input("Search item title (partial match ok): ").strip()
    cur.execute(
        """
        SELECT i.itemID, i.title, i.status,
               CASE WHEN pb.itemID IS NOT NULL THEN 'PrintBook'
                    WHEN ob.itemID IS NOT NULL THEN 'OnlineBook'
                    WHEN mg.itemID IS NOT NULL THEN 'Magazine'
                    WHEN jr.itemID IS NOT NULL THEN 'Journal'
                    WHEN rc.itemID IS NOT NULL THEN 'Recording'
               END AS itemType
        FROM Item i
        LEFT JOIN PrintBook  pb ON pb.itemID = i.itemID
        LEFT JOIN OnlineBook ob ON ob.itemID = i.itemID
        LEFT JOIN Magazine   mg ON mg.itemID = i.itemID
        LEFT JOIN Journal    jr ON jr.itemID = i.itemID
        LEFT JOIN Recording  rc ON rc.itemID = i.itemID
        WHERE i.title LIKE ?
        ORDER BY i.itemID
        """,
        (f"%{keyword}%",),
    )
    rows = cur.fetchall()
    if not rows:
        print("No items found.\n")
        return
    print(f"\n{'itemID':<8}{'title':<30}{'type':<12}{'status':<12}")
    for itemID, title, status, itemType in rows:
        print(f"{itemID:<8}{title:<30}{itemType:<12}{status:<12}")
    print()


def borrow_item(conn, cur):
    itemID = input("Item ID to borrow: ").strip()
    personID = input("Your member ID: ").strip()

    cur.execute("SELECT status FROM Item WHERE itemID = ?", (itemID,))
    row = cur.fetchone()
    if not row:
        print(f"No item with ID {itemID}.\n")
        return
    if row[0] != "Available":
        print(f"Item {itemID} is not available (status: {row[0]}).\n")
        return

    today = date.today().isoformat()
    cur.execute(
        "INSERT INTO Loan (itemID, personID, loanDate, dueDate) VALUES (?, ?, ?, date(?, ?))",
        (itemID, personID, today, today, f"+{LOAN_PERIOD_DAYS} days"),
    )
    conn.commit()
    print(f"Borrowed {itemID}. Due back in {LOAN_PERIOD_DAYS} days.\n")


def return_item(conn, cur):
    itemID = input("Item ID to return: ").strip()

    cur.execute(
        "SELECT personID, loanDate, dueDate FROM Loan WHERE itemID = ? AND returnDate IS NULL",
        (itemID,),
    )
    row = cur.fetchone()
    if not row:
        print(f"No active loan found for item {itemID}.\n")
        return
    personID, loanDate, dueDate = row

    today = date.today().isoformat()
    cur.execute(
        "UPDATE Loan SET returnDate = ? WHERE itemID = ? AND personID = ? AND loanDate = ?",
        (today, itemID, personID, loanDate),
    )

    if today > dueDate:
        cur.execute(
            "SELECT 1 FROM Fine WHERE itemID = ? AND personID = ? AND loanDate = ?",
            (itemID, personID, loanDate),
        )
        already_fined = cur.fetchone() is not None
        days_late = (date.fromisoformat(today) - date.fromisoformat(dueDate)).days
        if already_fined:
            print(f"Returned {itemID} {days_late} day(s) late. A fine was already on file for this loan.\n")
        else:
            amount = round(days_late * FINE_RATE_PER_DAY, 2)
            cur.execute(
                "INSERT INTO Fine (itemID, personID, loanDate, amountOwed, dateIssued) VALUES (?, ?, ?, ?, ?)",
                (itemID, personID, loanDate, amount, today),
            )
            print(f"Returned {itemID} {days_late} day(s) late. Fine issued: ${amount:.2f}\n")
    else:
        print(f"Returned {itemID} on time. Thanks!\n")

    conn.commit()


def donate_item(conn, cur):
    title = input("Title of the donated item: ").strip()
    donorID = input("Donor's member ID (leave blank if unknown): ").strip() or None

    print("Item type: 1) PrintBook 2) OnlineBook 3) Magazine 4) Journal 5) Recording")
    choice = input("Choose type: ").strip()
    if choice not in ITEM_TYPES:
        print("Invalid type.\n")
        return
    tableName, fields = ITEM_TYPES[choice]

    values = {}
    for field in fields:
        values[field] = input(f"  {field}: ").strip()

    itemID = next_item_id(cur)
    today = date.today().isoformat()
    cur.execute(
        "INSERT INTO Item (itemID, title, acquisitionMethod, dateAdded, status, donatedBy) "
        "VALUES (?, ?, 'Donated', ?, 'Available', ?)",
        (itemID, title, today, donorID),
    )

    if tableName in ("PrintBook", "OnlineBook"):
        isbn = values["ISBN"]
        cur.execute("SELECT 1 FROM Book WHERE ISBN = ?", (isbn,))
        if not cur.fetchone():
            author = input("  New ISBN - author: ").strip()
            publisher = input("  New ISBN - publisher: ").strip()
            cur.execute(
                "INSERT INTO Book (ISBN, author, publisher) VALUES (?, ?, ?)",
                (isbn, author, publisher),
            )
        if tableName == "PrintBook":
            cur.execute(
                "INSERT INTO PrintBook (itemID, ISBN, shelfLocation) VALUES (?, ?, ?)",
                (itemID, isbn, values["shelfLocation"]),
            )
        else:
            cur.execute(
                "INSERT INTO OnlineBook (itemID, ISBN, fileFormat, accessURL) VALUES (?, ?, ?, ?)",
                (itemID, isbn, values["fileFormat"], values["accessURL"]),
            )
    elif tableName == "Magazine":
        cur.execute(
            "INSERT INTO Magazine (itemID, issueNumber, publicationDate, publisher) VALUES (?, ?, ?, ?)",
            (itemID, values["issueNumber"], values["publicationDate"], values["publisher"]),
        )
    elif tableName == "Journal":
        cur.execute(
            "INSERT INTO Journal (itemID, volume, issueNumber, subjectArea) VALUES (?, ?, ?, ?)",
            (itemID, values["volume"], values["issueNumber"], values["subjectArea"]),
        )
    elif tableName == "Recording":
        cur.execute(
            "INSERT INTO Recording (itemID, artist, format, duration) VALUES (?, ?, ?, ?)",
            (itemID, values["artist"], values["format"], values["duration"]),
        )

    conn.commit()
    print(f"Donated item added as {itemID}.\n")


def main():
    conn = connect()
    cur = conn.cursor()
    menu = """
1) Find an item
2) Borrow an item
3) Return an item
4) Donate an item
5) Exit
"""
    actions = {
        "1": lambda: find_item(cur),
        "2": lambda: borrow_item(conn, cur),
        "3": lambda: return_item(conn, cur),
        "4": lambda: donate_item(conn, cur),
    }
    while True:
        print(menu)
        choice = input("Choose an option: ").strip()
        if choice == "5":
            break
        action = actions.get(choice)
        if action:
            action()
        else:
            print("Invalid option.\n")
    conn.close()


if __name__ == "__main__":
    main()
