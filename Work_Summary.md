# Work Summary — Person A and Person B Contributions

A record of who built what across the project, current as of `main` @ `be8a7d5`
(2026-08-10). Compiled by Person B from the git history and the audit trail.

---

## Project overview

A library database in SQLite with a Python menu application, split into two
clusters:

- **Person A** (`seungyeopshin` / `syshinvan`, repo owner, `SY_branch`) — the
  **item cluster**: Item and its five subclasses (PrintBook, OnlineBook,
  Magazine, Journal, Recording), Loan, Fine, AcquisitionCandidate.
- **Person B** (`jreech2005`, `VC_branch`) — the **people cluster**: Person,
  Member, Staff, Volunteer, Room, Event, AudienceGroup, RecommendedFor, Attends.

Each half has its own Steps 1–6 (spec, ERD, BCNF analysis, schema, data, app).
The halves join through three cross-cluster foreign keys, a unified
`Step6_App.py`, a shared `build_db.py`, and the generated submission PDF
(`mp.pdf`, built by `build_mp_pdf.py`).

---

## Person A's contributions

- **Jul 9–26** — repo setup, README with the team task split, then the complete
  item-cluster Steps 1–6 in one drop (`64327d5`): schema with
  checkout/return/fine triggers, 10+ rows per table, and an app with
  find/borrow/return/donate features, all parameterized SQL.
- **Aug 7 (PR #1, `c485d20`)** — the integration commit: enabled the three
  cross-cluster foreign keys, created the unified `Step6_App.py` that serves
  both halves' features over one connection, cleaned up docs.
- **Aug 10 (PR #4, `d35efb9`)** — fixed the bulk of Person B's audit:
  concurrent-loan trigger, five disjoint-subclass triggers,
  date/donor/numeric/title CHECK constraints, the `WHEN NEW.returnDate IS NULL`
  checkout-trigger fix (removing the data-file repair UPDATE), `find_item`'s
  `ELSE 'Unknown'`, suspended/unknown-member rejection on borrow, numeric-safe
  item ID generation, error handling in the standalone app, the ERD 1:1
  arrowhead, and a Known Limitations section in Step 3.

## Person B's contributions

- **Aug 6 — the complete people-cluster half** (`24e5970`…`1f46bd3`): spec, ERD
  script and rendered diagram, BCNF analysis, schema with room-booking and
  event-capacity triggers, data authored to cover every person ID Person A's
  data references, and the app half (find event, register, volunteer, ask a
  librarian). Plus project infrastructure: `build_db.py` with the agreed load
  order (B schema → A schema → B data → A data), untracking the `library.db`
  build artifact, documenting the ID contract (P001–P010 members, P020–P025
  donors, P001–P007 suggesters), and app hardening (numeric-safe ID generation,
  script-relative DB path).
- **Aug 10 — integration polish (PR #2)**: ERD corrections (By connected to the
  Member entity, total-participation double lines, notation key), AudienceGroup
  widened to ten groups with each referenced in RecommendedFor,
  single-head-of-library triggers, a portable font search replacing the
  hardcoded path in the PDF builder, and documented known limitations in
  Step 3.
- **Aug 10 — the audit** (`Audit_PersonA.md`, `55afcac`): 25 issues in
  Person A's half (22 original + 3 post-merge findings), every one confirmed by
  running code against a throwaway database — four crash bugs, five
  silent-data-corruption bugs, design gaps, and doc contradictions — with a
  prioritized fix-order table, a post-merge re-test of all 22 against merged
  main, and the open items filed as issue #3.
- **Aug 10 — closing out the audit** (`be8a7d5`): verified every fix in
  Person A's `d35efb9` empirically (rebuilt the database, re-ran the audit's
  sad-path battery, drove both apps with scripted input), then fixed the two
  remaining open items directly (see below), updated Step 3's limitations,
  rebuilt `mp.pdf`, and merged to `main`.

## Person B's contributions to Person A's half

1. **The audit that drove Person A's fix commit.** `Audit_PersonA.md` is the
   document `d35efb9` was written against: every issue live-tested, prioritized
   by effort, with the working fix suggested for each (the
   `WHEN NEW.returnDate IS NULL` trigger guard, the `ELSE 'Unknown'` CASE arm,
   the donor CHECK, the `main()` error wrapper). It also credited what was
   solid: parameterized SQL throughout, a correct lossless Book decomposition,
   internally consistent data.
2. **Independent verification of Person A's fixes.** After `d35efb9` landed,
   the audit's own failing tests were re-run against a rebuilt database —
   concurrent loans, dual-subclass inserts, historical returned loans,
   purchased-with-donor, backwards dates, non-numeric durations, empty titles,
   expired-member borrows, bad-format donations, Ctrl-D — confirming each now
   rejects cleanly or degrades gracefully.
3. **Direct fixes in Person A's files** (`be8a7d5`, with sign-off, per the
   team's rule that each half's files belong to their owner): rewrote
   `Fine_Requires_Overdue_Loan` in `Step4_PersonA_Schema.sql` to judge
   overdueness by the fine's own `dateIssued` instead of `date('now')` — making
   the data load deterministic on any build date (issue 11) — and added
   `sync_overdue_loans()` to `Step6_PersonA_App.py`, wired into both apps at
   startup, so past-due Active loans actually move to Overdue (issue 10; on
   first run it caught a sixth overdue loan the hand-typed statuses had
   missed). Updated `Step3_PersonA_BCNF.md`'s Known Limitations to match.
4. **Infrastructure Person A's half depends on**: the `build_db.py` load order
   that lets Person A's foreign keys resolve against Person B's data; Person B
   data deliberately covering every ID Person A's rows reference; untracking
   Person A's committed `library.db` (audit issue 22); the portable font search
   in the shared PDF builder (`b56c456`); and `Integration_Notes.md`
   documenting the fixes for the hardcoded ERD output path and the Loan→Member
   reference before Person A applied them.

---

## Current state

- `main` = `VC_branch` at the time of writing; all work pushed.
- All 25 audit items are fixed and verified, except two intentionally kept as
  documented limitations in `Step3_PersonA_BCNF.md`: total participation of the
  Item isa hierarchy (unenforceable by trigger in SQLite — the Item row and its
  subclass row are separate INSERTs) and per-copy title duplication (fixing it
  would mean a cross-half schema redesign).
- `build_db.py` reports `foreign_key_check: ok` / `integrity_check: ok`; both
  the unified and standalone apps pass happy- and sad-path testing.
