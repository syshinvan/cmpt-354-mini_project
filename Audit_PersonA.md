# Review of Person A's Half — Plain-Language Audit

Every issue marked **[tested]** was confirmed by actually running the code against a
throwaway copy of the database, not just by reading it. Nothing in Person A's files
has been changed — this is a report only.

> **Update 2026-08-10:** the halves are now merged (`main` at `42ff4fb`). Every issue
> below was re-tested against merged main — see the **Post-merge re-test** section at
> the end for what's resolved, what's still open, and the full happy/sad-path results.
> The open items are filed as issue #3 on the repo.

---

## Part 1: Things that make the app crash

These all show the user a raw Python error dump instead of a friendly message.

### 1. Pressing Ctrl-C or Ctrl-D kills the app **[tested]**
The app asks for input in many places but never plans for the user cancelling.
Pressing Ctrl-D (or the input simply running out, when testing with a script) crashes
it instantly with `EOFError`.
**Fix:** wrap the menu loop and prompts in `try/except` for `EOFError` and
`KeyboardInterrupt`, and print a goodbye message instead.

### 2. Donating a recording with the "wrong" format crashes **[tested]**
The database only allows recording formats CD, Vinyl, or DVD. If the user types
"Cassette", the database correctly refuses — but the app doesn't catch the refusal,
so it crashes with `sqlite3.IntegrityError`.
**Fix:** wrap each menu action in `try/except sqlite3.Error`, roll back, and print
the error as a normal message. One wrapper in `main()` fixes this whole category.

### 3. Searching can crash if an item has no type **[tested]**
`find_item` figures out an item's type (PrintBook, Magazine, ...) by checking which
subclass table it appears in. If an item is in none of them, the type comes back as
"nothing" (NULL), and printing "nothing" in a formatted column crashes with
`TypeError`. This can really happen because nothing forces every item to have a type
(see issue 7).
**Fix:** add an `ELSE 'Unknown'` to the CASE in the SQL, or wrap the value in
`COALESCE(...)` before printing.

### 4. A guaranteed crash after we merge
Borrowing and donating never check that the person ID the user typed actually
exists. Right now that "works" (see issue 5). The moment we turn on the three
foreign keys for the merge, a typo'd member ID will make the database refuse the
insert — and with no error handling, the app will crash every time.
**Fix:** look up the person first and print "no such member" — same pattern my
`register_event` uses.

---

## Part 2: Things that quietly put wrong data in the database

No crash here — worse, everything *looks* fine while the data goes bad.

### 5. You can borrow a book as a person who doesn't exist **[tested]**
I borrowed item IT001 as "P999" (nobody). The app happily said "Borrowed IT001."
That loan now points at a person who isn't in the database. Extra danger: if any of
these orphan loans exist when we enable the foreign keys, the database's own
consistency check will fail and block the merge.

### 6. The same book can be on loan to two people at once **[tested]**
The app checks availability before borrowing, but the database itself doesn't, so a
second loan can slip in (another app, direct SQL, a bug). Once that happens it
snowballs: `return_item` grabs "the" active loan **without an ORDER BY**, so it
returns an arbitrary one of the two — and the return-trigger then marks the item
"Available" even though the *other* person still has it out. I reproduced this whole
chain.
**Fix:** a trigger that refuses a new loan while the item already has an open loan,
and an `ORDER BY` on the return lookup.

### 7. "Every item is exactly one type" is promised but not enforced **[tested]**
The README says the item types are *disjoint and total*: every item is exactly one
of the five kinds. The database doesn't enforce either half — I inserted one item
that was both a PrintBook *and* a Magazine, and another item that was no type at
all. Both were accepted. There's also no "known limitations" note admitting this.
**Fix:** either add triggers, or (acceptable for this course) a written
"known limitations" section saying it's not enforced and why.

### 8. Loading old, already-returned loans corrupts item statuses **[tested]**
The checkout trigger fires on *every* new loan row — even a historical one that's
already returned. Inserting a returned loan for IT008 flipped IT008 to "CheckedOut"
even though nobody has it. Person A actually hit this themselves: their own data
file needs a repair UPDATE (line 166) to undo the trigger's damage after loading.
That repair query is the symptom, not the cure.
**Fix:** make the trigger fire only `WHEN NEW.returnDate IS NULL`.

### 9. A purchased item can have a "donor" **[tested]**
The schema comment says donatedBy is "set only if Donated", but nothing checks it —
I inserted a Purchased item with a donor and it was accepted. This one is a one-line
fix: `CHECK (acquisitionMethod = 'Donated' OR donatedBy IS NULL)`.

---

## Part 3: Design gaps (no crash, no corruption — just drift)

10. **The "Overdue" status is decorative.** The five Overdue loans in the data were
    typed in by hand; nothing ever moves a loan from Active to Overdue when its due
    date passes, so the status stops matching reality over time.
11. **Loading the data depends on today's date.** The fine trigger compares against
    `date('now')`, so rebuilding the database *before* 2026-06-24 would have rejected
    five of the ten fines. It only loads cleanly today because those due dates are
    now in the past.
12. **Missing cheap sanity checks:** nothing requires a due date after the loan date,
    a return date after the loan date, or that a "Paid" fine actually has a paid
    date.

---

## Part 4: Smaller app problems

13. A **suspended member can still borrow** (and nothing checks the borrower is a
    member at all — related to our agreed Loan→Member decision).
14. The app opens `library.db` **relative to wherever you run it from**. Run it from
    another folder and sqlite silently creates a fresh empty file, then everything
    fails with "no such table". (My app shares this to match — worth fixing in both
    during the merge with `os.path.dirname(os.path.abspath(__file__))`.)
15. **Item IDs break at the 1,000th item.** IDs are compared as text, and
    `'IT999' > 'IT1000'` alphabetically, so the generator would reuse IT1000 and
    crash on a duplicate key. Unlikely in this course, but it's a real latent bug.
16. **Numbers aren't validated:** donating a recording with duration "abc" stores
    the literal text "abc" in a numeric column.

---

## Part 5: The ERD

17. **The script only runs on Person A's laptop.** The output path is hardcoded to
    `/Users/seungyeopshin/Desktop/...`, so it crashes anywhere else. The fix (build
    the path from the script's own location) is written up in
    `Integration_Notes.md`, and my Step 2 script shows the pattern.
18. **The Loan–Fine arrow says the wrong thing.** The README says one loan has at
    most one fine (1:1), but the diagram has an arrow only on the Loan side — in
    this notation that reads as "a loan can have many fines". A second arrowhead
    into Fine is missing.
19. Cosmetic: the README calls the relationship "Borrows"; the diagram splits it
    into "By" and "For" without a note connecting the names.

---

## Part 6: Documents disagreeing with each other

20. **Who can borrow?** Person A's own Step 1 says "Members can borrow items", but
    their schema comment says the loan references *Person*. We've settled this
    (it's **Member**, per the README); the exact two-line fix is in
    `Integration_Notes.md`.
21. **A repeated-title anomaly the BCNF write-up misses.** Titles live in the Item
    table, so two copies of the same book store the same title twice — 8 ISBNs in
    Person A's own data do this. It's exactly the duplication problem their Book
    table fixes for authors and publishers, left unfixed for titles. The write-up's
    closing claim ("no other attribute determines another") holds only because it
    never looks across tables. Deserves at least a stated assumption.
22. `library.db` (a generated file) was committed to git. Already fixed on
    `VC_branch`: it's untracked and in `.gitignore`; rebuild anytime with
    `python3 build_db.py`.

---

## What's genuinely good

- **Every SQL statement is parameterized** — no injection risk anywhere.
- The **Book decomposition in Step 3 is correct** (lossless, dependency-preserving),
  and the data actually demonstrates why it's needed.
- I verified by query that the data is **internally consistent**: no shared ISBN has
  mismatched titles or authors, and every table meets the 10-row minimum.
- The ERD notation is consistent and cleanly laid out.

---

## Suggested fix order

| Priority | Issues | Effort |
|---|---|---|
| 1. One error-handling wrapper in `main()` | 1, 2, 4 | ~10 lines |
| 2. Validate person IDs before inserting | 4, 5 | ~6 lines |
| 3. `ELSE 'Unknown'` in the find query | 3 | 1 line |
| 4. `WHEN NEW.returnDate IS NULL` on the checkout trigger (and drop the data-file repair UPDATE) | 8 | 2 lines |
| 5. Donor/purchase CHECK | 9 | 1 line |
| 6. Everything else | 6, 7, 10–19 | fix or document as known limitations |

---

# Post-merge re-test (2026-08-10, `main` @ `42ff4fb`)

Both halves are merged. I re-ran the whole audit against the merged code: drove the
unified `Step6_App.py` through every feature with scripted input (happy paths and
~30 sad paths), then fired a constraint battery at the schema in raw SQL. The
database was rebuilt afterward, so none of the test rows persist.

## Where the 22 issues stand now

| Status | Issues |
|---|---|
| **Resolved** | 4, 5 (FKs enabled — orphan borrowers now rejected), 14 (script-relative DB path), 17 (script-relative ERD path), 20 (Loan→Member everywhere), 22 (`library.db` untracked, `.gitignore` in place) |
| **Partially resolved** | 1, 2 (the unified `Step6_App.py` wraps every action in `except sqlite3.Error` / `except EOFError, KeyboardInterrupt` with rollback — but the standalone `Step6_PersonA_App.py` `main()` is still bare), 13 (the Member FK now forces the borrower to *be* a member; suspended members still borrow) |
| **Still open** | 3, 6, 7, 8, 9, 10, 11, 12, 15, 16, 18, 19, 21 — all re-confirmed live below |

## Happy paths — all eight features work

Find/borrow/return/donate items, find/register events, volunteer, and ask-a-librarian
all succeed end to end on a fresh build. A borrow→return round-trips the item's
status correctly, event search shows the widened ten-group audiences, and
`build_db.py` reports `foreign_key_check: ok` / `integrity_check: ok` throughout.

## Sad paths that are now handled correctly

- Invalid menu options, no-match searches, and an SQL-injection-shaped keyword
  (`%' OR 1=1--`) — parameterization holds, the keyword is treated as literal text.
- Borrow: nonexistent item, unavailable item, nonexistent person (P999), and a
  non-member (staff P013) — the last two are FK rejections, caught and rolled back.
- Return: no active loan, and double-return — clean messages.
- Donate: nonexistent donor (FK rejection with full rollback — no orphan Item row)
  and an invalid recording format ("Cassette") — the old issue-2 crash is now a
  friendly "Database error … Nothing was changed."
- Register: unknown person, unknown event, duplicate registration, and a **full
  event** (E011) — the capacity trigger fires and the wrapper catches it.
- Volunteer: unknown ID, blank name/email, already-a-volunteer, duplicate email
  (UNIQUE on `Person.email` rejects it, rolled back).
- Ctrl-D mid-action prints "Cancelled; nothing was changed"; at the menu, "Goodbye!".
- Schema battery — all ten hostile inserts rejected: second head of the library,
  supervisor cycle, room double-booking, negative salary, malformed date, backwards
  event times, zero-capacity room, out-of-domain audience group, over-capacity
  registration, fine on a non-overdue loan.

## Sad paths that still fail (re-confirmed on merged main)

- **Issue 3 is now the only way to crash the merged app** — and it still does. A
  typeless item (which issue 7 still lets in) makes `find_item` throw
  `TypeError: unsupported format string passed to NoneType.__format__`. The unified
  wrapper only catches `sqlite3.Error`, so this sails through and kills the app.
- **Issue 6**: a second concurrent loan on a checked-out item is accepted in SQL.
- **Issue 7**: an item with no subclass row, and an item in two subclasses, both
  accepted.
- **Issue 8**: inserting a historical already-returned loan flipped the item
  Available → CheckedOut. The data-file repair UPDATE is still masking this.
- **Issue 9**: a Purchased item with a donor is still accepted.
- **Issue 12**: a loan with `dueDate` before `loanDate` is still accepted.
- **Issue 13**: suspended member P010 borrowed successfully.
- **Issue 16**: recording duration `"abc"` is stored as literal text in the INT
  column.

## New findings from this round

23. **An empty-string title is accepted when donating** — `NOT NULL` doesn't stop
    `''`, so a nameless item lands in the catalogue. Same input-validation family
    as issue 16.
24. **The borrow prompts read both inputs before validating either** — typing a bad
    item ID still costs you the member-ID prompt before the error appears. Cosmetic,
    but it makes scripted/piped use of the app fragile.
25. **FK rejections surface as raw constraint text** — "FOREIGN KEY constraint
    failed" instead of "no such member". No crash and no bad data, but the friendly
    lookup the original issue-4 fix asked for is still worth doing.
