-- Step 4: SQL Schema (Person A: Item / Loan / Fine / AcquisitionCandidate)
-- Person/Member are Person B's tables. Load order: Person B schema -> this file -> Person B data -> Person A data.

PRAGMA foreign_keys = ON;

-- ==== Item + isa subclasses ====

CREATE TABLE Item (
    itemID              CHAR(20)  PRIMARY KEY,
    title               CHAR(100) NOT NULL CHECK (length(trim(title)) > 0),
    acquisitionMethod   CHAR(10)  NOT NULL CHECK (acquisitionMethod IN ('Purchased','Donated')),
    dateAdded           DATE      NOT NULL CHECK (date(dateAdded) IS NOT NULL),
    status              CHAR(15)  NOT NULL DEFAULT 'Available'
                                  CHECK (status IN ('Available','CheckedOut','Lost')),
    donatedBy           CHAR(20),                         -- FK -> Person, set only if Donated
    CHECK (acquisitionMethod = 'Donated' OR donatedBy IS NULL),
    FOREIGN KEY (donatedBy) REFERENCES Person(personID)
);

CREATE TABLE Book (
    ISBN                CHAR(20)  PRIMARY KEY,
    author              CHAR(100) NOT NULL,
    publisher           CHAR(100)
);

CREATE TABLE PrintBook (
    itemID              CHAR(20)  PRIMARY KEY,
    ISBN                CHAR(20)  NOT NULL,
    shelfLocation       CHAR(20),
    FOREIGN KEY (itemID) REFERENCES Item(itemID),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN)
);

CREATE TABLE OnlineBook (
    itemID              CHAR(20)  PRIMARY KEY,
    ISBN                CHAR(20)  NOT NULL,
    fileFormat          CHAR(10),
    accessURL           CHAR(200),
    FOREIGN KEY (itemID) REFERENCES Item(itemID),
    FOREIGN KEY (ISBN) REFERENCES Book(ISBN)
);

CREATE TABLE Magazine (
    itemID              CHAR(20)  PRIMARY KEY,
    issueNumber         INT,
    publicationDate     DATE,
    publisher           CHAR(100),
    FOREIGN KEY (itemID) REFERENCES Item(itemID)
);

CREATE TABLE Journal (
    itemID              CHAR(20)  PRIMARY KEY,
    volume              INT,
    issueNumber         INT,
    subjectArea         CHAR(50),
    FOREIGN KEY (itemID) REFERENCES Item(itemID)
);

CREATE TABLE Recording (
    itemID              CHAR(20)  PRIMARY KEY,
    artist              CHAR(100),
    format              CHAR(10) CHECK (format IN ('CD','Vinyl','DVD')),
    duration            INT CHECK (duration IS NULL
                                   OR (typeof(duration) IN ('integer','real') AND duration >= 0)),  -- seconds
    FOREIGN KEY (itemID) REFERENCES Item(itemID)
);

-- ==== Loan (weak entity) ====

CREATE TABLE Loan (
    itemID              CHAR(20)  NOT NULL,
    personID            CHAR(20)  NOT NULL,               -- FK -> Member
    loanDate            DATE      NOT NULL CHECK (date(loanDate) IS NOT NULL),
    dueDate             DATE      NOT NULL CHECK (date(dueDate) IS NOT NULL),
    returnDate          DATE,                              -- null until returned
    status              CHAR(15)  NOT NULL DEFAULT 'Active'
                                  CHECK (status IN ('Active','Returned','Overdue')),
    CHECK (dueDate >= loanDate),
    CHECK (returnDate IS NULL OR returnDate >= loanDate),
    PRIMARY KEY (itemID, personID, loanDate),
    FOREIGN KEY (itemID) REFERENCES Item(itemID),
    FOREIGN KEY (personID) REFERENCES Member(personID)
);

-- ==== Fine (weak entity) ====

CREATE TABLE Fine (
    itemID              CHAR(20)  NOT NULL,
    personID            CHAR(20)  NOT NULL,
    loanDate            DATE      NOT NULL,
    amountOwed          DECIMAL(6,2) NOT NULL
                                  CHECK (typeof(amountOwed) IN ('integer','real') AND amountOwed >= 0),
    dateIssued          DATE      NOT NULL CHECK (date(dateIssued) IS NOT NULL),
    datePaid            DATE,                              -- null until paid
    status              CHAR(10)  NOT NULL DEFAULT 'Unpaid'
                                  CHECK (status IN ('Unpaid','Paid','Waived')),
    CHECK (status <> 'Paid' OR datePaid IS NOT NULL),
    CHECK (datePaid IS NULL OR datePaid >= dateIssued),
    PRIMARY KEY (itemID, personID, loanDate),
    FOREIGN KEY (itemID, personID, loanDate) REFERENCES Loan(itemID, personID, loanDate)
);

-- ==== AcquisitionCandidate ====

CREATE TABLE AcquisitionCandidate (
    candidateID         CHAR(20)  PRIMARY KEY,
    proposedTitle       CHAR(100) NOT NULL,
    format              CHAR(15),
    status              CHAR(10)  NOT NULL DEFAULT 'Pending'
                                  CHECK (status IN ('Pending','Approved','Rejected')),
    dateProposed        DATE      NOT NULL CHECK (date(dateProposed) IS NOT NULL),
    estimatedCost       DECIMAL(8,2) CHECK (estimatedCost IS NULL
                                   OR (typeof(estimatedCost) IN ('integer','real') AND estimatedCost >= 0)),
    suggestedBy         CHAR(20),                          -- FK -> Person
    FOREIGN KEY (suggestedBy) REFERENCES Person(personID)
);

-- ==== Triggers ====

-- an item cannot be on loan to two people at once
CREATE TRIGGER Loan_No_Concurrent_Checkout
BEFORE INSERT ON Loan
BEGIN
    SELECT CASE
        WHEN EXISTS (
            SELECT 1 FROM Loan WHERE itemID = NEW.itemID AND returnDate IS NULL
        )
        THEN RAISE(ABORT, 'Error: this item is already on an active loan!')
    END;
END;

-- new loan -> item becomes CheckedOut (only for a currently-active loan; loading a
-- historical already-returned loan must not flip a since-returned item back)
CREATE TRIGGER Loan_Checkout
AFTER INSERT ON Loan
WHEN NEW.returnDate IS NULL
BEGIN
    UPDATE Item SET status = 'CheckedOut' WHERE itemID = NEW.itemID;
END;

-- returned -> item becomes Available
CREATE TRIGGER Loan_Return
AFTER UPDATE OF returnDate ON Loan
WHEN NEW.returnDate IS NOT NULL AND OLD.returnDate IS NULL
BEGIN
    UPDATE Item SET status = 'Available' WHERE itemID = NEW.itemID;
    UPDATE Loan SET status = 'Returned' WHERE itemID = NEW.itemID AND personID = NEW.personID AND loanDate = NEW.loanDate;
END;

-- only allow a Fine on an overdue loan
CREATE TRIGGER Fine_Requires_Overdue_Loan
BEFORE INSERT ON Fine
BEGIN
    SELECT CASE
        WHEN NOT EXISTS (
            SELECT 1 FROM Loan
            WHERE itemID = NEW.itemID AND personID = NEW.personID AND loanDate = NEW.loanDate
              AND (
                    (returnDate IS NULL AND dueDate < date('now'))
                 OR (returnDate IS NOT NULL AND returnDate > dueDate)
              )
        )
        THEN RAISE(ABORT, 'Error: a Fine can only be issued for an overdue loan!')
    END;
END;

-- Item's isa hierarchy is disjoint (Step 1: every item is exactly one of the five
-- kinds): each subclass insert checks that itemID is not already in any of the
-- other four. (Every item having at least one subclass row is not enforceable here:
-- the Item row and its subclass row are two separate INSERTs, so there is no single
-- point in time at which a trigger could see both; see Step 3's known limitations.)
CREATE TRIGGER PrintBook_Disjoint
BEFORE INSERT ON PrintBook
BEGIN
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM OnlineBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Magazine WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Journal WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Recording WHERE itemID = NEW.itemID
    ) THEN RAISE(ABORT, 'Error: this item is already a different item type!') END;
END;

CREATE TRIGGER OnlineBook_Disjoint
BEFORE INSERT ON OnlineBook
BEGIN
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM PrintBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Magazine WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Journal WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Recording WHERE itemID = NEW.itemID
    ) THEN RAISE(ABORT, 'Error: this item is already a different item type!') END;
END;

CREATE TRIGGER Magazine_Disjoint
BEFORE INSERT ON Magazine
BEGIN
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM PrintBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM OnlineBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Journal WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Recording WHERE itemID = NEW.itemID
    ) THEN RAISE(ABORT, 'Error: this item is already a different item type!') END;
END;

CREATE TRIGGER Journal_Disjoint
BEFORE INSERT ON Journal
BEGIN
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM PrintBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM OnlineBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Magazine WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Recording WHERE itemID = NEW.itemID
    ) THEN RAISE(ABORT, 'Error: this item is already a different item type!') END;
END;

CREATE TRIGGER Recording_Disjoint
BEFORE INSERT ON Recording
BEGIN
    SELECT CASE WHEN EXISTS (
        SELECT 1 FROM PrintBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM OnlineBook WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Magazine WHERE itemID = NEW.itemID
        UNION SELECT 1 FROM Journal WHERE itemID = NEW.itemID
    ) THEN RAISE(ABORT, 'Error: this item is already a different item type!') END;
END;
