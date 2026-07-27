-- Step 4 — SQL Schema (Person A: Item / Loan / Fine / AcquisitionCandidate)
-- Person/Member are Person B's tables; their FKs are commented out until merged.

PRAGMA foreign_keys = ON;

-- ==== Item + isa subclasses ====

CREATE TABLE Item (
    itemID              CHAR(20)  PRIMARY KEY,
    title               CHAR(100) NOT NULL,
    acquisitionMethod   CHAR(10)  NOT NULL CHECK (acquisitionMethod IN ('Purchased','Donated')),
    dateAdded           DATE      NOT NULL,
    status              CHAR(15)  NOT NULL DEFAULT 'Available'
                                  CHECK (status IN ('Available','CheckedOut','Lost')),
    donatedBy           CHAR(20)                          -- FK -> Person, set only if Donated
    -- FOREIGN KEY (donatedBy) REFERENCES Person(personID)
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
    duration            INT,                              -- seconds
    FOREIGN KEY (itemID) REFERENCES Item(itemID)
);

-- ==== Loan (weak entity) ====

CREATE TABLE Loan (
    itemID              CHAR(20)  NOT NULL,
    personID            CHAR(20)  NOT NULL,               -- FK -> Person
    loanDate            DATE      NOT NULL,
    dueDate             DATE      NOT NULL,
    returnDate          DATE,                              -- null until returned
    status              CHAR(15)  NOT NULL DEFAULT 'Active'
                                  CHECK (status IN ('Active','Returned','Overdue')),
    PRIMARY KEY (itemID, personID, loanDate),
    FOREIGN KEY (itemID) REFERENCES Item(itemID)
    -- FOREIGN KEY (personID) REFERENCES Person(personID)
);

-- ==== Fine (weak entity) ====

CREATE TABLE Fine (
    itemID              CHAR(20)  NOT NULL,
    personID            CHAR(20)  NOT NULL,
    loanDate            DATE      NOT NULL,
    amountOwed          DECIMAL(6,2) NOT NULL CHECK (amountOwed >= 0),
    dateIssued          DATE      NOT NULL,
    datePaid            DATE,                              -- null until paid
    status              CHAR(10)  NOT NULL DEFAULT 'Unpaid'
                                  CHECK (status IN ('Unpaid','Paid','Waived')),
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
    dateProposed        DATE      NOT NULL,
    estimatedCost       DECIMAL(8,2) CHECK (estimatedCost >= 0),
    suggestedBy         CHAR(20)                           -- FK -> Person
    -- FOREIGN KEY (suggestedBy) REFERENCES Person(personID)
);

-- ==== Triggers ====

-- new loan -> item becomes CheckedOut
CREATE TRIGGER Loan_Checkout
AFTER INSERT ON Loan
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
