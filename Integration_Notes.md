# Integration Notes (Person B → Person A)

## 1. The ID contract between the two halves

Derived by loading `Step4_PersonA_Schema.sql` + `Step5_PersonA_Data.sql` into SQLite and
querying every distinct personID that Person A's data references:

| Referenced from | IDs |
|---|---|
| `Loan.personID` | P001–P010 |
| `Fine.personID` | P001–P010 (same loans) |
| `AcquisitionCandidate.suggestedBy` | P001–P007 |
| `Item.donatedBy` | P020–P025 |

`Step5_PersonB_Data.sql` therefore guarantees:

- **P001–P010, P020–P025 all exist in `Person`** (16 IDs, part of a 30-person roster).
- **P001–P010 are also `Member` rows**, because they borrow: we agreed Borrows follows
  README §3/§4, so `Loan.personID` references **Member**, not Person. (Person A's inline
  comment on `Loan.personID` says "FK -> Person"; that comment is the out-of-date side
  of the disagreement; see the edit below.)

## 2. Exact edits to enable Person A's three foreign keys

All three are in `Step4_PersonA_Schema.sql`. In each case the line above the commented
FK needs a trailing comma when the FK becomes a real constraint.

**Item.donatedBy** (lines 15–16):

```sql
    donatedBy           CHAR(20),                         -- FK -> Person, set only if Donated
    FOREIGN KEY (donatedBy) REFERENCES Person(personID)
```

**Loan.personID** (lines 77–78): note this references `Member`, per README §3/§4
(Loan is a weak entity supported by Member; only members can borrow):

```sql
    FOREIGN KEY (itemID) REFERENCES Item(itemID),
    FOREIGN KEY (personID) REFERENCES Member(personID)
```

Also update the comment on line 70 from `-- FK -> Person` to `-- FK -> Member`.

**AcquisitionCandidate.suggestedBy** (lines 106–107):

```sql
    suggestedBy         CHAR(20),                          -- FK -> Person
    FOREIGN KEY (suggestedBy) REFERENCES Person(personID)
```

These exact edits were tested: the merged database builds cleanly with all three FKs
enabled (`PRAGMA foreign_key_check` and `PRAGMA integrity_check` both pass), and loans
by non-members, unknown donors, and unknown suggesters are then rejected at insert time.

## 3. Required load order

```
1. Step4_PersonB_Schema.sql   (Person must exist before anything references it)
2. Step4_PersonA_Schema.sql
3. Step5_PersonB_Data.sql     (Person/Member rows before loans/donations point at them)
4. Step5_PersonA_Data.sql
```

`build_db.py` builds `library.db` in exactly this order and then runs
`PRAGMA foreign_key_check` + `PRAGMA integrity_check`, exiting non-zero on any failure.
The order already matters today (both apps share one `library.db`) and becomes mandatory
once the FKs above are enabled.

## 4. Housekeeping

- `library.db` is a build artifact: it is now in `.gitignore` and was removed from git
  tracking (the working copy is untouched; rebuild any time with `python3 build_db.py`).
- `Step2_PersonA_ERD.py` writes its output to a hardcoded absolute path
  (`/Users/seungyeopshin/Desktop/...`), so it crashes on other machines. Suggested fix,
  mirroring `Step2_PersonB_ERD.py`: derive the output directory from
  `os.path.dirname(os.path.abspath(__file__))`.
