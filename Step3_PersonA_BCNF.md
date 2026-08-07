# Step 3: BCNF Proof (Person A's cluster: Item / Loan / Fine / AcquisitionCandidate)

## 0. Converting the ERD (Step 2) to relations

Each non-weak entity set becomes its own relation. The isa hierarchy uses **Strategy 1 (straight
E/R)**: one relation per subclass holding the root key plus its own attributes. Many-one
relationships (`DonatedBy`, `Suggested`) are folded into the "many" side's relation instead of
getting their own relation. Weak entities carry the borrowed key(s) of their supporting entity set(s).

- **Item**(itemID, title, acquisitionMethod, dateAdded, status, donatedBy)
- **PrintBook**(itemID, ISBN, author, publisher, shelfLocation)
- **OnlineBook**(itemID, ISBN, author, fileFormat, accessURL)
- **Magazine**(itemID, issueNumber, publicationDate, publisher)
- **Journal**(itemID, volume, issueNumber, subjectArea)
- **Recording**(itemID, artist, format, duration)
- **Loan**(itemID, personID, loanDate, dueDate, returnDate, status)
- **Fine**(itemID, personID, loanDate, amountOwed, dateIssued, datePaid, status)
- **AcquisitionCandidate**(candidateID, proposedTitle, format, status, dateProposed, estimatedCost, suggestedBy)

(`donatedBy` and `suggestedBy` are nullable FKs to Person, reflecting optional participation, so
folding them in causes no anomaly.)

---

## 1. Item(itemID, title, acquisitionMethod, dateAdded, status, donatedBy)

**FDs:** itemID → title, acquisitionMethod, dateAdded, status, donatedBy
No other attribute determines another (title doesn't fix acquisitionMethod, etc.).

**Candidate key:** {itemID}, since itemID⁺ = all attributes.
**BCNF check:** the only non-trivial FD has itemID (a key) on the left. **Already BCNF.**

---

## 2. PrintBook(itemID, ISBN, author, publisher, shelfLocation)

**FDs:**
- itemID → ISBN, author, publisher, shelfLocation (itemID is the key of every subclass relation)
- **ISBN → author, publisher** (real-world assumption: an ISBN identifies one published edition,
  so the same ISBN always has the same author and publisher, regardless of how many physical
  copies the library owns)

**Candidate key:** {itemID}.

**BCNF check:** is ISBN a superkey? No. The library can hold multiple physical copies of the same
book (same ISBN, different itemID, e.g. two copies of the same novel on different shelves), so
ISBN → author, publisher **violates BCNF**.

**Anomaly this causes if left alone:** author/publisher get repeated on every copy row; fixing a
typo in an author's name requires updating every copy of that book instead of one row (update
anomaly), and the redundant copies could drift out of sync.

**Decomposition:**
- **Book**(ISBN, author, publisher), PK = ISBN
- **PrintBook**(itemID, ISBN, shelfLocation), PK = itemID, FK: ISBN → Book

**Lossless-join check:** common attribute = ISBN, which is a key of `Book`, so the join is
lossless. **Dependency-preserving:** ISBN→author,publisher is enforced in `Book`; itemID→ISBN,
shelfLocation is enforced in the new `PrintBook`. Both original FDs are covered.

---

## 3. OnlineBook(itemID, ISBN, author, fileFormat, accessURL)

**FDs:**
- itemID → ISBN, author, fileFormat, accessURL
- **ISBN → author** (same real-world assumption as above: online copies of the same edition
  share the same author)

**Candidate key:** {itemID}. **BCNF check:** ISBN → author violates BCNF for the same reason as
PrintBook (the same ISBN can back multiple online copies/licenses, e.g. multiple simultaneous
e-book licenses of the same title).

**Decomposition:** reuse the same `Book(ISBN, author, publisher)` relation from PrintBook's
decomposition (author is the same fact regardless of format, so one shared table avoids storing
it twice):
- **OnlineBook**(itemID, ISBN, fileFormat, accessURL), PK = itemID, FK: ISBN → Book

Lossless (ISBN is the key of `Book`), and dependency-preserving for the same reason as above.

---

## 4. Magazine(itemID, issueNumber, publicationDate, publisher)

**FDs:** itemID → issueNumber, publicationDate, publisher.

Unlike ISBN for books, this schema has **no magazine-title identifier** in this relation
(issueNumber alone is ambiguous: issue #5 of two different magazines are unrelated), so there is
no attribute that determines publisher other than the full key.

**Candidate key:** {itemID}. **BCNF check:** only FD has a key on the left. **Already BCNF.**

---

## 5. Journal(itemID, volume, issueNumber, subjectArea)

**FDs:** itemID → volume, issueNumber, subjectArea. No journal-title identifier exists in this
relation either, so no other FD applies.

**Candidate key:** {itemID}. **Already BCNF.**

---

## 6. Recording(itemID, artist, format, duration)

**FDs:** itemID → artist, format, duration. artist does not determine format or duration (the same
artist can have recordings in different formats/lengths).

**Candidate key:** {itemID}. **Already BCNF.**

---

## 7. Loan(itemID, personID, loanDate, dueDate, returnDate, status)

**FDs:** {itemID, personID, loanDate} → dueDate, returnDate, status.

*Assumption:* dueDate is not assumed to be a strict function of loanDate alone (loan periods can
differ by item type or membership tier, and staff can grant extensions), so there is no smaller
determinant than the full weak key.

**Candidate key:** {itemID, personID, loanDate} (matches the weak entity's key from the ERD).
**BCNF check:** only FD has the full key on the left. **Already BCNF.**

---

## 8. Fine(itemID, personID, loanDate, amountOwed, dateIssued, datePaid, status)

**FDs:** {itemID, personID, loanDate} → amountOwed, dateIssued, datePaid, status (key borrowed
entirely from Loan, since Fine is 1:1 with Loan and contributes no partial key of its own).

*Assumption:* amountOwed is not assumed to be a strict function of dateIssued (fine policy/rate
can change over time or be manually waived/adjusted), so no smaller determinant exists.

**Candidate key:** {itemID, personID, loanDate}. **Already BCNF.**

---

## 9. AcquisitionCandidate(candidateID, proposedTitle, format, status, dateProposed, estimatedCost, suggestedBy)

**FDs:** candidateID → proposedTitle, format, status, dateProposed, estimatedCost, suggestedBy.
proposedTitle does not determine the rest (the same title could be proposed twice, in different
formats or at different times, as separate candidates).

**Candidate key:** {candidateID}. **Already BCNF.**

---

## Final BCNF Schema (Person A's cluster)

```
Item(itemID, title, acquisitionMethod, dateAdded, status, donatedBy)
Book(ISBN, author, publisher)
PrintBook(itemID, ISBN, shelfLocation)
OnlineBook(itemID, ISBN, fileFormat, accessURL)
Magazine(itemID, issueNumber, publicationDate, publisher)
Journal(itemID, volume, issueNumber, subjectArea)
Recording(itemID, artist, format, duration)
Loan(itemID, personID, loanDate, dueDate, returnDate, status)
Fine(itemID, personID, loanDate, amountOwed, dateIssued, datePaid, status)
AcquisitionCandidate(candidateID, proposedTitle, format, status, dateProposed, estimatedCost, suggestedBy)
```

Only one real decomposition was needed (Book split out of PrintBook/OnlineBook); every other
relation was already in BCNF because its only non-trivial FD already has the full key on the left.
No other attribute in this cluster determines another beyond what's explained by the primary key.
