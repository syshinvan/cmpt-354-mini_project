# Step 3: BCNF Proof (Person B's cluster: Person / Member / Staff / Volunteer / Room / Event / AudienceGroup / RecommendedFor / Attends)

## 0. Converting the ERD (Step 2) to relations

Same conversion rules as Person A's half. Each strong entity set becomes its own relation. The isa
hierarchy uses **Strategy 1 (straight E/R)**: one relation per subclass holding the root key plus its
own attributes: the right fit here because the hierarchy is overlapping + partial, so a person can
appear in several subclass relations or in none. Many-one relationships (`HeldIn`, `Supervises`) are
folded into the "many" side's relation: `HeldIn` becomes a NOT NULL `roomID` in Event (total
participation), and `Supervises` becomes a nullable `supervisorID` in Staff (the head of the library
has none). Many-many relationships (`RecommendedFor`, `Attends`) each get their own relation keyed
by the pair of participating keys.

- **Person**(personID, name, email, phone, address)
- **Member**(personID, membershipDate, membershipStatus)
- **Staff**(personID, role, hireDate, salary, supervisorID)
- **Volunteer**(personID, startDate, hoursLogged)
- **Room**(roomID, name, capacity)
- **Event**(eventID, title, description, eventType, eventDate, startTime, endTime, roomID)
- **AudienceGroup**(groupName)
- **RecommendedFor**(eventID, groupName)
- **Attends**(personID, eventID, registrationDate)

---

## 1. Person(personID, name, email, phone, address)

**FDs:**
- personID → name, email, phone, address
- **email → personID** (real-world assumption from the Step 1 spec: every person has a contact
  email and no two people share one, since email is how the library reaches a person about loans,
  fines, and registrations)

**Candidate keys:** {personID}, and also **{email}**, a second, non-obvious candidate key: from
email → personID and personID → everything, transitively email⁺ = all attributes. The schema
enforces it with NOT NULL UNIQUE on email.

**BCNF check:** both non-trivial FDs have a candidate key on the left (personID and email are each
keys). **Already BCNF.**

*Alternative assumption:* if shared household emails were allowed, email → personID would not hold;
email stops being a candidate key (and the UNIQUE constraint would have to go), but no FD with a
non-key determinant appears either way, so the relation stays in BCNF under both assumptions. name,
phone, and address determine nothing (two people can share any of them).

---

## 2. Member(personID, membershipDate, membershipStatus)

**FDs:** personID → membershipDate, membershipStatus. Neither membershipDate nor membershipStatus
determines anything (many people join the same day; many memberships share a status).

**Candidate key:** {personID}, since personID⁺ = all attributes.
**BCNF check:** the only non-trivial FD has a key on the left. **Already BCNF.**

---

## 3. Staff(personID, role, hireDate, salary, supervisorID)

**FDs:** personID → role, hireDate, salary, supervisorID.

*Assumption:* salary is negotiated per person, not fixed by job title (two Librarians hired in
different years earn different amounts), so role → salary does **not** hold, and no attribute other
than personID determines anything.

**Candidate key:** {personID}. **BCNF check:** only FD has a key on the left. **Already BCNF.**

*Alternative assumption and where it would break:* if the library instead paid on a rigid scale
where the job title fixes the pay, role → salary would hold with role not a superkey: a **BCNF
violation** (salary would be repeated on every staff row with that role: update anomaly). The
decomposition would be **RolePay**(role, salary) with PK = role, and
**Staff**(personID, role, hireDate, supervisorID) with an FK on role → RolePay. That join is
lossless (role is a key of RolePay) and dependency-preserving. We keep the per-person salary
design because it matches how the spec describes staff pay.

---

## 4. Volunteer(personID, startDate, hoursLogged)

**FDs:** personID → startDate, hoursLogged. Neither startDate nor hoursLogged determines anything.

**Candidate key:** {personID}. **Already BCNF.**

---

## 5. Room(roomID, name, capacity)

**FDs:** roomID → name, capacity.

*Assumption:* room names are **not** assumed unique (a future branch or renovation could produce two
"Meeting Room A"s), so name → roomID is not claimed. If names were assumed unique, {name} would be
another candidate key, and the relation would still be in BCNF, since name would then be a key.
capacity determines nothing (many rooms can seat 20).

**Candidate key:** {roomID}. **Already BCNF.**

---

## 6. Event(eventID, title, description, eventType, eventDate, startTime, endTime, roomID)

**FDs:**
- eventID → title, description, eventType, eventDate, startTime, endTime, roomID
- **{roomID, eventDate, startTime} → eventID** (real-world rule from the Step 1 spec: a room cannot
  be double-booked, so at most one event occupies a given room at a given date and start time)

**Candidate keys:** {eventID}, and also **{roomID, eventDate, startTime}**, the second, non-obvious
candidate key: it determines eventID, and eventID determines everything else, so its closure is all
attributes. The schema enforces it with UNIQUE(roomID, eventDate, startTime) (and the no-overlap
trigger enforces the stronger interval version of the rule).

**BCNF check:** both non-trivial FDs have a candidate key on the left. **Already BCNF.**

*Alternative assumption and where it would break:* the analysis does not assume anything like
"every BookClub lasts 90 minutes". If eventType → duration were real, endTime would be determined
by {eventType, startTime}, a non-superkey determinant: a BCNF violation whose fix would be
**TypeDuration**(eventType, duration) with endTime dropped from Event and recomputed on the join.
Event lengths genuinely vary here (Step 5 has 60-, 90-, and 360-minute events), so no such FD holds.

---

## 7. AudienceGroup(groupName)

Single-attribute relation; only trivial FDs exist. **Candidate key:** {groupName}.
**Trivially BCNF.**

---

## 8. RecommendedFor(eventID, groupName)

**FDs:** none that are non-trivial: the relation is all key. An event can be recommended for many
groups and a group can have many events, so neither attribute determines the other.

**Candidate key:** {eventID, groupName}. **BCNF check:** a relation with no non-trivial FDs cannot
violate BCNF. **Already BCNF.**

---

## 9. Attends(personID, eventID, registrationDate)

**FDs:** {personID, eventID} → registrationDate (a person registers for a given event at most once,
per the Step 1 spec, so the pair fixes the registration date).

*Assumption:* registrationDate is genuinely determined by the pair, not by either attribute alone
(one person registers for many events, and one event has many registrants, on assorted dates).

**Candidate key:** {personID, eventID}. **BCNF check:** only FD has the full key on the left.
**Already BCNF.**

---

## Why RecommendedFor and Attends are two relations, not one

Both hang off Event, so one could imagine a single combined relation
R(eventID, groupName, personID, registrationDate). That design is wrong because the two facts are
**independent**: which audience groups an event is aimed at has nothing to do with which individual
people have registered. In the combined relation this independence shows up as the multivalued
dependencies eventID ↠ groupName and eventID ↠ {personID, registrationDate}, a 4NF violation even
though no FD is violated. Concretely, an event recommended for 2 groups with 5 registrants needs
2 × 5 = 10 rows to stay consistent instead of 2 + 5 = 7, every new registrant must be repeated once
per group (redundancy + update anomaly), and an event with recommendations but no registrants yet
(or vice versa) forces NULLs into half the key. Keeping the two many-many relationships as separate
relations, exactly as the ERD draws them, avoids all of this.

---

## Final BCNF Schema (Person B's cluster)

```
Person(personID, name, email, phone, address)
Member(personID, membershipDate, membershipStatus)
Staff(personID, role, hireDate, salary, supervisorID)
Volunteer(personID, startDate, hoursLogged)
Room(roomID, name, capacity)
Event(eventID, title, description, eventType, eventDate, startTime, endTime, roomID)
AudienceGroup(groupName)
RecommendedFor(eventID, groupName)
Attends(personID, eventID, registrationDate)
```

No decomposition was needed: every non-trivial FD in this cluster already has a candidate key on
its left side. The two extra candidate keys found along the way, Person.{email} and
Event.{roomID, eventDate, startTime}, are declared as UNIQUE constraints in Step 4 so the schema
actually enforces what this analysis claims.

---

## Known limitations

Every Step 1 rule for this cluster is enforced in Step 4, but four of them cannot be expressed as
declarative constraints, because a SQLite CHECK can only see the row being written (there is no
`CREATE ASSERTION`, and subqueries are not allowed in CHECK). These are enforced by triggers instead:

- **No double-booking of a room** — an event overlapping another event in the same room requires
  comparing against other Event rows (`Event_No_Overlap_Insert/Update`).
- **Registrations cannot exceed room capacity** — counts Attends rows against Room.capacity, on
  every path that can break it: new registration, moved registration, event moved to a smaller
  room, room capacity shrunk (`Attends_Capacity`, `Attends_Capacity_Update`, `Event_Room_Capacity`,
  `Room_Capacity_Shrink`).
- **The supervision chain cannot loop** — the CHECK on Staff blocks only direct self-supervision; a
  longer cycle needs a recursive walk up the chain (`Staff_No_Supervisor_Cycle_Insert/Update`).
- **At most one head of the library** — "at most one row where supervisorID IS NULL" is not
  expressible as a CHECK, and a UNIQUE index does not help because NULLs never compare equal
  (`Staff_Single_Head_Insert/Update`).

What remains genuinely unenforced:

- The *existence* of a head is not guaranteed: the triggers stop a second supervisor-less staff row,
  but nothing stops deleting the head (or having an empty Staff table), so the schema enforces
  "at most one head", not Step 1's implied "exactly one".
- SQLite does not enforce `CHAR(n)` lengths (type affinity): the declared widths document intent and
  match Person A's schema, but over-long strings are not rejected.
