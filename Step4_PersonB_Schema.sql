-- Step 4 — SQL Schema (Person B: Person + subclasses / Room / Event / AudienceGroup / RecommendedFor / Attends)
-- Load this file BEFORE Step4_PersonA_Schema.sql: Person A's Item/Loan/AcquisitionCandidate
-- tables reference Person(personID) once their commented-out FKs are enabled.

PRAGMA foreign_keys = ON;

-- ==== Person + isa subclasses (overlapping + partial) ====

CREATE TABLE Person (
    personID            CHAR(20)  PRIMARY KEY,
    name                CHAR(100) NOT NULL,
    email               CHAR(100) NOT NULL UNIQUE,        -- second candidate key (Step 3, §1)
    phone               CHAR(20),
    address             CHAR(200)
);

CREATE TABLE Member (
    personID            CHAR(20)  PRIMARY KEY,
    membershipDate      DATE      NOT NULL,
    membershipStatus    CHAR(10)  NOT NULL DEFAULT 'Active'
                                  CHECK (membershipStatus IN ('Active','Expired','Suspended')),
    FOREIGN KEY (personID) REFERENCES Person(personID)
);

CREATE TABLE Staff (
    personID            CHAR(20)  PRIMARY KEY,
    role                CHAR(50)  NOT NULL,
    hireDate            DATE      NOT NULL,
    salary              DECIMAL(9,2) NOT NULL CHECK (salary >= 0),
    supervisorID        CHAR(20),                         -- null only for the head of the library
    CHECK (supervisorID IS NULL OR supervisorID <> personID),
    FOREIGN KEY (personID) REFERENCES Person(personID),
    FOREIGN KEY (supervisorID) REFERENCES Staff(personID)
);

CREATE TABLE Volunteer (
    personID            CHAR(20)  PRIMARY KEY,
    startDate           DATE      NOT NULL,
    hoursLogged         DECIMAL(7,1) NOT NULL DEFAULT 0 CHECK (hoursLogged >= 0),
    FOREIGN KEY (personID) REFERENCES Person(personID)
);

-- ==== Room / Event / AudienceGroup ====

CREATE TABLE Room (
    roomID              CHAR(20)  PRIMARY KEY,
    name                CHAR(50)  NOT NULL,
    capacity            INT       NOT NULL CHECK (capacity >= 1)
);

CREATE TABLE Event (
    eventID             CHAR(20)  PRIMARY KEY,
    title               CHAR(100) NOT NULL,
    description         CHAR(300),                        -- optional longer blurb
    eventType           CHAR(15)  NOT NULL
                                  CHECK (eventType IN ('BookClub','ArtShow','FilmScreening','Other')),
    eventDate           DATE      NOT NULL,               -- README's "date"; renamed so it cannot be confused with SQL's date() in triggers
    startTime           TIME      NOT NULL,
    endTime             TIME      NOT NULL,
    roomID              CHAR(20)  NOT NULL,               -- HeldIn is total: every event has a room
    CHECK (endTime > startTime),
    UNIQUE (roomID, eventDate, startTime),                -- second candidate key (Step 3, §6)
    FOREIGN KEY (roomID) REFERENCES Room(roomID)
);

CREATE TABLE AudienceGroup (
    groupName           CHAR(10)  PRIMARY KEY
                                  CHECK (groupName IN ('Kids','Teens','Adults','Seniors','AllAges'))
);

-- ==== RecommendedFor / Attends (many-many relationships) ====

CREATE TABLE RecommendedFor (
    eventID             CHAR(20)  NOT NULL,
    groupName           CHAR(10)  NOT NULL,
    PRIMARY KEY (eventID, groupName),
    FOREIGN KEY (eventID) REFERENCES Event(eventID),
    FOREIGN KEY (groupName) REFERENCES AudienceGroup(groupName)
);

CREATE TABLE Attends (
    personID            CHAR(20)  NOT NULL,
    eventID             CHAR(20)  NOT NULL,
    registrationDate    DATE      NOT NULL,
    PRIMARY KEY (personID, eventID),
    FOREIGN KEY (personID) REFERENCES Person(personID),
    FOREIGN KEY (eventID) REFERENCES Event(eventID)
);

-- ==== Triggers (rules that depend on other rows) ====

-- a room cannot be double-booked: reject an event that overlaps an existing one
-- in the same room on the same date (intervals [start,end) touch but may not cross)
CREATE TRIGGER Event_No_Overlap_Insert
BEFORE INSERT ON Event
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM Event
            WHERE roomID = NEW.roomID AND eventDate = NEW.eventDate
              AND startTime < NEW.endTime AND endTime > NEW.startTime
        )
        THEN RAISE(ABORT, 'Error: the room is already booked for an overlapping event!')
    END;
END;

CREATE TRIGGER Event_No_Overlap_Update
BEFORE UPDATE OF roomID, eventDate, startTime, endTime ON Event
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM Event
            WHERE eventID <> NEW.eventID
              AND roomID = NEW.roomID AND eventDate = NEW.eventDate
              AND startTime < NEW.endTime AND endTime > NEW.startTime
        )
        THEN RAISE(ABORT, 'Error: the room is already booked for an overlapping event!')
    END;
END;

-- registrations cannot exceed the capacity of the event's room
CREATE TRIGGER Attends_Capacity
BEFORE INSERT ON Attends
BEGIN
    SELECT CASE
        WHEN (SELECT COUNT(*) FROM Attends WHERE eventID = NEW.eventID)
             >= (SELECT r.capacity FROM Room r
                 JOIN Event e ON e.roomID = r.roomID
                 WHERE e.eventID = NEW.eventID)
        THEN RAISE(ABORT, 'Error: this event has reached the capacity of its room!')
    END;
END;

-- ==== Known limitations (stated rules SQLite cannot fully enforce here) ====
-- * SQLite does not enforce CHAR(n) lengths (type affinity): the declared widths match
--   Person A's schema and document intent, but over-long strings are not rejected.
-- * DATE/TIME values are ISO-8601 text; the CHECKs compare them as strings, which is
--   correct for the 'YYYY-MM-DD' / 'HH:MM' formats used throughout, but a malformed
--   date string would not be rejected by the schema itself.
-- * The capacity rule is enforced on registration (the only path the app uses).
--   Shrinking Room.capacity, or moving an already-full event to a smaller room, below
--   the current registration count is not blocked and would need a staff-side check.
