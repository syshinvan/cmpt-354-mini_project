-- Step 5: Populate Tables (Person A: Item / Loan / Fine / AcquisitionCandidate)
-- Run after Step4_PersonA_Schema.sql and Step5_PersonB_Data.sql. personID values
-- (P001..) reference real rows in Person B's Person/Member table; see Integration_Notes.md.

-- ==== Book (12 rows; a few ISBNs are reused by multiple copies below) ====
INSERT INTO Book (ISBN, author, publisher) VALUES
('ISBN001', 'J. Carter',    'Horizon Press'),
('ISBN002', 'M. Alvarez',   'Bluepoint Books'),
('ISBN003', 'R. Chen',      'TechScribe'),
('ISBN004', 'L. Nguyen',    'Horizon Press'),
('ISBN005', 'S. Ito',       'Maple Leaf Publishing'),
('ISBN006', 'D. Okafor',    'Bluepoint Books'),
('ISBN007', 'E. Brandt',    'TechScribe'),
('ISBN008', 'P. Kim',       'Maple Leaf Publishing'),
('ISBN009', 'A. Singh',     'Horizon Press'),
('ISBN010', 'K. Reyes',     'Bluepoint Books'),
('ISBN011', 'N. Dubois',    'Maple Leaf Publishing'),
('ISBN012', 'T. Osei',      'TechScribe');

-- ==== Item (50 rows: 10 per subclass) ====
INSERT INTO Item (itemID, title, acquisitionMethod, dateAdded, status, donatedBy) VALUES
-- PrintBook (IT001-IT010)
('IT001', 'The Great Adventure',       'Purchased', '2024-03-01', 'Available', NULL),
('IT002', 'Silent Rivers',             'Purchased', '2024-03-05', 'Available', NULL),
('IT003', 'The Last Algorithm',        'Purchased', '2024-04-10', 'Available', NULL),
('IT004', 'Whispers of the Past',      'Donated',   '2024-05-15', 'Available', 'P020'),
('IT005', 'The Great Adventure',       'Purchased', '2024-06-01', 'Available', NULL),
('IT006', 'Garden of Echoes',          'Purchased', '2024-06-20', 'Available', NULL),
('IT007', 'Beyond the Horizon',        'Donated',   '2024-07-01', 'Available', 'P021'),
('IT008', 'The Clockmaker''s Secret',  'Purchased', '2024-08-11', 'Available', NULL),
('IT009', 'Silent Rivers',             'Purchased', '2024-09-01', 'Available', NULL),
('IT010', 'Ocean of Stars',            'Purchased', '2024-09-20', 'Lost',      NULL),
-- OnlineBook (IT011-IT020)
('IT011', 'Digital Frontiers',         'Purchased', '2024-03-10', 'Available', NULL),
('IT012', 'The Quiet Storm',           'Purchased', '2024-03-15', 'Available', NULL),
('IT013', 'The Last Algorithm',        'Purchased', '2024-04-15', 'Available', NULL),
('IT014', 'Learning to Fly',           'Purchased', '2024-05-01', 'Available', NULL),
('IT015', 'Fragments of Time',         'Donated',   '2024-05-20', 'Available', 'P022'),
('IT016', 'Whispers of the Past',      'Purchased', '2024-06-05', 'Available', NULL),
('IT017', 'Digital Frontiers',         'Purchased', '2024-06-25', 'Available', NULL),
('IT018', 'Garden of Echoes',          'Purchased', '2024-07-10', 'Available', NULL),
('IT019', 'Beyond the Horizon',        'Purchased', '2024-08-01', 'Available', NULL),
('IT020', 'The Quiet Storm',           'Purchased', '2024-08-15', 'Available', NULL),
-- Magazine (IT021-IT030)
('IT021', 'National Geographic',       'Purchased', '2026-01-15', 'Available', NULL),
('IT022', 'National Geographic',       'Purchased', '2026-02-15', 'Available', NULL),
('IT023', 'Time',                      'Purchased', '2026-03-01', 'Available', NULL),
('IT024', 'Time',                      'Purchased', '2026-03-08', 'Available', NULL),
('IT025', 'The Economist',             'Purchased', '2026-02-20', 'Available', NULL),
('IT026', 'Wired',                     'Purchased', '2026-01-30', 'Available', NULL),
('IT027', 'Wired',                     'Purchased', '2026-02-28', 'Available', NULL),
('IT028', 'Scientific American',       'Donated',   '2026-01-10', 'Available', 'P023'),
('IT029', 'Popular Mechanics',         'Purchased', '2026-02-05', 'Available', NULL),
('IT030', 'Vogue',                     'Purchased', '2026-03-01', 'Available', NULL),
-- Journal (IT031-IT040)
('IT031', 'Journal of Computer Science Research', 'Purchased', '2025-09-01', 'Available', NULL),
('IT032', 'Journal of Computer Science Research', 'Purchased', '2025-10-01', 'Available', NULL),
('IT033', 'Annals of Biology',                    'Purchased', '2025-09-15', 'Available', NULL),
('IT034', 'Journal of Modern Physics',            'Purchased', '2025-10-10', 'Available', NULL),
('IT035', 'Journal of Modern Physics',             'Purchased', '2025-11-10', 'Available', NULL),
('IT036', 'Review of Economic Studies',            'Purchased', '2025-09-20', 'Available', NULL),
('IT037', 'Psychology Today Journal',              'Donated',   '2025-10-05', 'Available', 'P024'),
('IT038', 'Journal of Environmental Science',      'Purchased', '2025-11-01', 'Available', NULL),
('IT039', 'Linguistics Quarterly',                 'Purchased', '2025-09-25', 'Available', NULL),
('IT040', 'Journal of Art History',                'Purchased', '2025-10-15', 'Available', NULL),
-- Recording (IT041-IT050)
('IT041', 'Moonlight Sessions',        'Purchased', '2024-11-01', 'Available', NULL),
('IT042', 'Echoes of Tomorrow',        'Purchased', '2024-11-15', 'Available', NULL),
('IT043', 'Vinyl Dreams',              'Purchased', '2024-12-01', 'Available', NULL),
('IT044', 'City Lights Live',          'Donated',   '2024-12-10', 'Available', 'P025'),
('IT045', 'Analog Heart',              'Purchased', '2025-01-05', 'Available', NULL),
('IT046', 'Symphony No. 5 Recording',  'Purchased', '2025-01-20', 'Available', NULL),
('IT047', 'Live at the Grove',         'Purchased', '2025-02-01', 'Available', NULL),
('IT048', 'Retro Waves',               'Purchased', '2025-02-15', 'Available', NULL),
('IT049', 'Jazz Standards Vol. 2',     'Purchased', '2025-03-01', 'Available', NULL),
('IT050', 'Acoustic Sessions',         'Purchased', '2025-03-10', 'Lost',      NULL);

-- ==== PrintBook (10) ====
INSERT INTO PrintBook (itemID, ISBN, shelfLocation) VALUES
('IT001','ISBN001','A-101'),
('IT002','ISBN002','A-102'),
('IT003','ISBN003','B-201'),
('IT004','ISBN004','B-202'),
('IT005','ISBN001','A-103'),
('IT006','ISBN005','C-301'),
('IT007','ISBN006','C-302'),
('IT008','ISBN007','D-401'),
('IT009','ISBN002','A-104'),
('IT010','ISBN008','D-402');

-- ==== OnlineBook (10) ====
INSERT INTO OnlineBook (itemID, ISBN, fileFormat, accessURL) VALUES
('IT011','ISBN009','EPUB','https://library.example.org/ebooks/digital-frontiers'),
('IT012','ISBN010','PDF', 'https://library.example.org/ebooks/quiet-storm'),
('IT013','ISBN003','EPUB','https://library.example.org/ebooks/last-algorithm'),
('IT014','ISBN011','EPUB','https://library.example.org/ebooks/learning-to-fly'),
('IT015','ISBN012','PDF', 'https://library.example.org/ebooks/fragments-of-time'),
('IT016','ISBN004','EPUB','https://library.example.org/ebooks/whispers-of-the-past'),
('IT017','ISBN009','MOBI','https://library.example.org/ebooks/digital-frontiers-2'),
('IT018','ISBN005','PDF', 'https://library.example.org/ebooks/garden-of-echoes'),
('IT019','ISBN006','EPUB','https://library.example.org/ebooks/beyond-the-horizon'),
('IT020','ISBN010','PDF', 'https://library.example.org/ebooks/quiet-storm-2');

-- ==== Magazine (10) ====
INSERT INTO Magazine (itemID, issueNumber, publicationDate, publisher) VALUES
('IT021',245,'2026-01-15','NatGeo Society'),
('IT022',246,'2026-02-15','NatGeo Society'),
('IT023',12, '2026-03-01','Time USA'),
('IT024',13, '2026-03-08','Time USA'),
('IT025',402,'2026-02-20','Economist Group'),
('IT026',88, '2026-01-30','Conde Nast'),
('IT027',89, '2026-02-28','Conde Nast'),
('IT028',330,'2026-01-10','Springer Nature'),
('IT029',201,'2026-02-05','Hearst'),
('IT030',155,'2026-03-01','Conde Nast');

-- ==== Journal (10) ====
INSERT INTO Journal (itemID, volume, issueNumber, subjectArea) VALUES
('IT031',14,2,'Computer Science'),
('IT032',14,3,'Computer Science'),
('IT033',8, 1,'Biology'),
('IT034',22,4,'Physics'),
('IT035',22,5,'Physics'),
('IT036',45,1,'Economics'),
('IT037',30,2,'Psychology'),
('IT038',11,3,'Environmental Science'),
('IT039',19,1,'Linguistics'),
('IT040',6, 2,'Art History');

-- ==== Recording (10) ====
INSERT INTO Recording (itemID, artist, format, duration) VALUES
('IT041','The Wandering Keys','CD',    2580),
('IT042','Nova Rae',          'CD',    3120),
('IT043','The Wandering Keys','Vinyl', 2400),
('IT044','Marcus Idle',       'DVD',   5400),
('IT045','Sienna Frost',      'Vinyl', 2700),
('IT046','City Philharmonic', 'CD',    2100),
('IT047','Nova Rae',          'DVD',   6000),
('IT048','The Analog Kids',   'Vinyl', 2350),
('IT049','Marcus Idle',       'CD',    2900),
('IT050','Sienna Frost',      'CD',    2200);

-- ==== Loan (14: mix of active/on-time, returned-on-time, overdue, returned-late) ====
INSERT INTO Loan (itemID, personID, loanDate, dueDate, returnDate, status) VALUES
-- currently checked out, not yet due
('IT002','P001','2026-07-10','2026-08-10',NULL,'Active'),
('IT021','P002','2026-07-15','2026-08-15',NULL,'Active'),
('IT041','P003','2026-07-20','2026-08-20',NULL,'Active'),
-- returned on time
('IT031','P004','2026-06-01','2026-06-15','2026-06-14','Returned'),
-- overdue, still not returned
('IT003','P005','2026-05-01','2026-05-15',NULL,'Overdue'),
('IT022','P006','2026-05-10','2026-05-24',NULL,'Overdue'),
('IT042','P007','2026-05-20','2026-06-03',NULL,'Overdue'),
('IT032','P008','2026-06-01','2026-06-15',NULL,'Overdue'),
('IT004','P009','2026-06-10','2026-06-24',NULL,'Overdue'),
-- returned late
('IT005','P010','2026-04-01','2026-04-15','2026-05-01','Returned'),
('IT023','P001','2026-04-05','2026-04-19','2026-04-30','Returned'),
('IT043','P002','2026-04-10','2026-04-24','2026-05-05','Returned'),
('IT033','P003','2026-04-15','2026-04-29','2026-05-10','Returned'),
('IT006','P004','2026-04-20','2026-05-04','2026-05-20','Returned');

-- Loan_Checkout trigger flips every loaned item to CheckedOut; fix items whose
-- loan(s) are all returned back to Available.
UPDATE Item SET status = 'Available'
WHERE itemID IN (
    SELECT itemID FROM Loan GROUP BY itemID
    HAVING SUM(CASE WHEN returnDate IS NULL THEN 1 ELSE 0 END) = 0
);

-- ==== Fine (10: one per overdue/late loan above) ====
INSERT INTO Fine (itemID, personID, loanDate, amountOwed, dateIssued, datePaid, status) VALUES
('IT003','P005','2026-05-01',7.50,'2026-07-26',NULL,'Unpaid'),
('IT022','P006','2026-05-10',6.00,'2026-07-26',NULL,'Unpaid'),
('IT042','P007','2026-05-20',5.50,'2026-07-26',NULL,'Unpaid'),
('IT032','P008','2026-06-01',4.00,'2026-07-26',NULL,'Unpaid'),
('IT004','P009','2026-06-10',3.50,'2026-07-26',NULL,'Unpaid'),
('IT005','P010','2026-04-01',8.00,'2026-05-01','2026-05-10','Paid'),
('IT023','P001','2026-04-05',5.50,'2026-04-30','2026-05-05','Paid'),
('IT043','P002','2026-04-10',6.50,'2026-05-05',NULL,'Unpaid'),
('IT033','P003','2026-04-15',5.00,'2026-05-10','2026-05-15','Paid'),
('IT006','P004','2026-04-20',4.50,'2026-05-20',NULL,'Waived');

-- ==== AcquisitionCandidate (10) ====
INSERT INTO AcquisitionCandidate (candidateID, proposedTitle, format, status, dateProposed, estimatedCost, suggestedBy) VALUES
('AC001','The Silent Orbit',        'Print Book',            'Pending', '2026-07-01', 24.99, 'P001'),
('AC002','Coastal Memories',        'Online Book',           'Approved','2026-06-15', 14.99, NULL),
('AC003','Quantum Tales',           'Print Book',            'Rejected','2026-05-20', 29.99, 'P002'),
('AC004','The Modern Kitchen',      'Magazine Subscription', 'Approved','2026-06-01', 59.99, 'P003'),
('AC005','Journal of AI Ethics',    'Journal Subscription',  'Pending', '2026-07-10',199.99, NULL),
('AC006','Midnight Sonatas',        'CD',                    'Approved','2026-06-20', 18.50, 'P004'),
('AC007','The Forgotten Path',      'Print Book',            'Pending', '2026-07-15', 22.00, 'P005'),
('AC008','Desert Bloom',            'Vinyl',                 'Rejected','2026-05-05', 35.00, NULL),
('AC009','Global Politics Weekly',  'Magazine Subscription', 'Pending', '2026-07-05', 79.99, 'P006'),
('AC010','The Art of Silence',      'Online Book',           'Approved','2026-06-25', 12.99, 'P007');
