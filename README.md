# Mini Project — Library Database: Entity/Relationship Draft (v0)

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

- **Loan** — a weak entity that depends on both Member and Item (the same person can borrow the same item multiple times over separate periods, so a plain relationship isn't enough — each borrowing event needs its own instance).
  - Weak key: (personID, itemID, loanDate), or a surrogate loanID
  - Attributes: dueDate, returnDate (nullable), status
- **Fine** — a weak entity that depends on Loan (only exists for an overdue loan, 1:1 and optional).
  - Weak key: loanID
  - Attributes: amountOwed, dateIssued, datePaid (nullable), status (Unpaid/Paid/Waived)

## 4. Relationships — varied multiplicity/participation

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

---

## 5. Open questions to confirm with the team

- [ ] Should Item really be split into these 5 isa subclasses, or would a single `type` attribute be simpler? (isa better demonstrates "entity/relationship variety," but adds 5+1 tables in Step 4)
- [ ] Should we keep all 3 Person subclasses (Member/Staff/Volunteer), or cut down to 2 (Member/Staff) if time is short?
- [ ] Should Loan be modeled as a weak entity, or would a plain entity with a surrogate key (loanID) be simpler? (Either works, as long as it's justified in the Step 3 BCNF proof.)
- [ ] Should Event subtypes (BookClub/ArtShow/FilmScreening) also be isa subclasses, or is an `eventType` attribute enough? (We already used isa twice for Person and Item, so keeping Event as an attribute is probably enough for the variety requirement.)
- [ ] How should an AcquisitionCandidate that gets approved turn into an actual Item? (Likely just application logic — shouldn't affect the DB design much.)
- [ ] Is there anything more complex than necessary? (Design principle from Module 4: Simplicity — don't over-engineer.)

## 6. Next steps
1. Agree on the checklist above → split Step 2 (drawing the ERD) by domain:
   - **Person A**: Item (+ subclasses) / Loan / Fine / AcquisitionCandidate
   - **Person B**: Person (+ subclasses) / Event / Room / AudienceGroup / Attends
2. Each person draws their sub-diagram, then merge them (overlap points: Person↔Loan, Person↔Attends, Item↔DonatedBy)
3. Proceed to Step 3 (FD/BCNF proof) using the merged ERD
