# Mini Project: Library Database (Entity/Relationship Draft)

---

## 1. Entities (Strong Entities)

| Entity | Key | Attributes |
|---|---|---|
| **Person** | personID | name, email, phone, address |
| **Item** | itemID | title, acquisitionMethod (Purchased/Donated), dateAdded, status (Available/CheckedOut/Lost) |
| **Room** | roomID | name, capacity |
| **Event** | eventID | title, description, eventType (BookClub/ArtShow/FilmScreening/Other), date, startTime, endTime |
| **AudienceGroup** | groupName | (Kids/Teens/Adults/Seniors/AllAges) |
| **AcquisitionCandidate** | candidateID | proposedTitle, format, status (Pending/Approved/Rejected), dateProposed, estimatedCost |

## 2. Subclasses (isa hierarchies)

### 2-1. Person → Member / Staff / Volunteer
- Designed as **overlapping + partial** participation: a person can be a Member and a Staff/Volunteer at the same time, and can also belong to none of these subclasses (e.g., someone who only attends events).
- **Member** (personID) + membershipDate, membershipStatus
- **Staff** (personID) + role, hireDate, salary, supervisorID (self-referencing FK → another Staff.personID)
- **Volunteer** (personID) + startDate, hoursLogged

### 2-2. Item → PrintBook / OnlineBook / Magazine / Journal / Recording
- **Disjoint + total** participation: every Item is exactly one of these five.
- **PrintBook** (itemID) + ISBN, author, publisher, shelfLocation
- **OnlineBook** (itemID) + ISBN, author, fileFormat, accessURL
- **Magazine** (itemID) + issueNumber, publicationDate, publisher
- **Journal** (itemID) + volume, issueNumber, subjectArea
- **Recording** (itemID) + artist, format (CD/Vinyl/DVD), duration

## 3. Weak Entities

- **Loan**: a weak entity that depends on both Member and Item (the same person can borrow the same item multiple times over separate periods, so a plain relationship isn't enough; each borrowing event needs its own instance).
  - Weak key: (personID, itemID, loanDate), or a surrogate loanID
  - Attributes: dueDate, returnDate (nullable), status
- **Fine**: a weak entity that depends on Loan (only exists for an overdue loan, 1:1 and optional).
  - Weak key: loanID
  - Attributes: amountOwed, dateIssued, datePaid (nullable), status (Unpaid/Paid/Waived)

## 4. Relationships

| Relationship | Participants | Multiplicity | Participation |
|---|---|---|---|
| Supervises | Staff → Staff (self-referencing) | many-one | optional (the director has no supervisor) |
| Borrows (→ Loan weak entity) | Member, Item | many-many (can repeat over time) | optional on both sides |
| IncursFine | Loan → Fine | 1:1 | optional (no fine unless overdue) |
| HeldIn | Event → Room | many-one | **total** (every event must have a room) |
| RecommendedFor | Event ↔ AudienceGroup | many-many | optional |
| Attends | Person ↔ Event | many-many, attribute: registrationDate | optional |
| DonatedBy | Item → Person | many-one | optional (purchased items have none) |
| Suggested | AcquisitionCandidate → Person | many-one | optional (the suggester may be unknown) |

"Borrows" is the informal name for the Loan weak entity's two identifying relationships on the
ERDs: `By` (Loan → Member) and `For` (Loan → Item).

---

## 5. Team Task Split

Split by domain, not by step. Each person owns their half end-to-end.

- **Person A**: Item (+ subclasses: PrintBook/OnlineBook/Magazine/Journal/Recording) / Loan / Fine / AcquisitionCandidate
- **Person B**: Person (+ subclasses: Member/Staff/Volunteer) / Event / Room / AudienceGroup / Attends

Overlap points both people need to agree on: Person↔Loan (Borrows), Person↔Attends, Item↔DonatedBy (Person side).

| Step | Person A | Person B | Do together |
|---|---|---|---|
| 1. Specs | Write item/borrowing/fine/acquisition paragraphs | Write people/event/room paragraphs | Merge into one doc |
| 2. ERD | Draw Item cluster sub-diagram | Draw Person/Event cluster sub-diagram | Merge diagrams at the 3 overlap points above |
| 3. BCNF | Find FDs + BCNF proof for Item cluster tables | Find FDs + BCNF proof for Person cluster tables | Check FDs that cross the overlap relationships together |
| 4. SQL Schema | Write CREATE TABLE + constraints for their tables | Same for their tables | Agree on FK naming/types before either starts |
| 5. Populate | Insert ≥10 rows for their tables | Insert ≥10 rows for their tables | Make sure FK values reference real rows on both sides |
| 6. App (after Jul 20) | Implement: find item, borrow, return, donate | Implement: find event, register, volunteer, ask librarian | Integrate into one app, shared DB connection code |

## 6. Next steps
1. Split Step 2 (ERD) per the table above; each person draws their sub-diagram.
2. Merge diagrams at the overlap points, then proceed to Step 3 (BCNF) using the merged ERD.
