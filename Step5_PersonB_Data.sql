-- Step 5 — Populate Tables (Person B: Person + subclasses / Room / Event / AudienceGroup / RecommendedFor / Attends)
-- Run after Step4_PersonB_Schema.sql (and before Step5_PersonA_Data.sql when merging).
-- Covers every personID Person A's data references: P001-P010 borrow and get fined
-- (so they are Members), P001-P007 suggest acquisitions, P020-P025 donate items.

-- ==== Person (30 rows) ====
-- isa hierarchy is overlapping + partial (README §2-1); the data demonstrates both:
--   * overlapping: P002 is Member+Staff, P005 and P012 are Member+Volunteer,
--     P016 is Staff+Volunteer
--   * partial: P025 (donor only) and P026 (event attendee only) are in NO subclass
INSERT INTO Person (personID, name, email, phone, address) VALUES
('P001', 'Olivia Bennett',   'olivia.bennett@fastmail.com',  '604-555-0101', '1284 W 12th Ave, Vancouver'),
('P002', 'Ethan Walsh',      'ethan.walsh@gmail.com',        '604-555-0102', '450 Granville St, Vancouver'),
('P003', 'Maya Krishnan',    'maya.krishnan@outlook.com',    '778-555-0103', '2210 Cambie St, Vancouver'),
('P004', 'Lucas Ferreira',   'lucas.ferreira@gmail.com',     '604-555-0104', '881 Kingsway, Vancouver'),
('P005', 'Hana Sato',        'hana.sato@protonmail.com',     '778-555-0105', '3390 Oak St, Vancouver'),
('P006', 'Gabriel Moreau',   'g.moreau@telus.net',           '604-555-0106', '156 E 3rd Ave, Vancouver'),
('P007', 'Priya Anand',      'priya.anand@gmail.com',        '778-555-0107', '4021 Fraser St, Vancouver'),
('P008', 'Daniel Osei',      'daniel.osei@yahoo.com',        '604-555-0108', '77 Lonsdale Ave, North Vancouver'),
('P009', 'Sofia Lindqvist',  'sofia.lindqvist@gmail.com',    '604-555-0109', '1500 Marine Dr, West Vancouver'),
('P010', 'Marcus Yee',       'marcus.yee@outlook.com',       '778-555-0110', '6511 No. 3 Rd, Richmond'),
('P011', 'Amara Diallo',     'amara.diallo@gmail.com',       '604-555-0111', '3050 Main St, Vancouver'),
('P012', 'Leo Tanaka',       'leo.tanaka@shaw.ca',           '778-555-0112', '925 Denman St, Vancouver'),
('P013', 'Eleanor Voss',     'eleanor.voss@library.org',     '604-555-0113', '2833 W 41st Ave, Vancouver'),
('P014', 'Omar Haddad',      'omar.haddad@library.org',      '604-555-0114', '1177 Hornby St, Vancouver'),
('P015', 'Grace Liu',        'grace.liu@library.org',        NULL,           '5488 Victoria Dr, Vancouver'),
('P016', 'Victor Ramos',     'victor.ramos@library.org',     '778-555-0116', '333 Seymour St, Vancouver'),
('P017', 'Nadia Petrov',     'nadia.petrov@library.org',     '604-555-0117', '2020 Commercial Dr, Vancouver'),
('P018', 'Samuel Adeyemi',   'samuel.adeyemi@library.org',   '778-555-0118', '740 Nicola St, Vancouver'),
('P019', 'Isabelle Roy',     'isabelle.roy@library.org',     '604-555-0119', '4880 Dunbar St, Vancouver'),
('P020', 'Charlotte Mercer', 'charlotte.mercer@library.org', '604-555-0120', '1622 W Broadway, Vancouver'),
('P021', 'Felix Nguyen',     'felix.nguyen@gmail.com',       '778-555-0121', '8033 Granville St, Vancouver'),
('P022', 'Rosa Delgado',     'rosa.delgado@hotmail.com',     '604-555-0122', '2145 E Hastings St, Vancouver'),
('P023', 'Arjun Mehta',      'arjun.mehta@gmail.com',        '778-555-0123', '10160 152 St, Surrey'),
('P024', 'Ingrid Solberg',   'ingrid.solberg@icloud.com',    '604-555-0124', '1199 Seymour St, Vancouver'),
('P025', 'Tomas Rivera',     'tomas.rivera@gmail.com',       '778-555-0125', '3211 Grandview Hwy, Vancouver'),
('P026', 'June Park',        'june.park@naver.com',          NULL,           '5900 No. 1 Rd, Richmond'),
('P027', 'David Klein',      'david.klein@library.org',      '604-555-0127', '2688 Arbutus St, Vancouver'),
('P028', 'Wendy Zhao',       'wendy.zhao@gmail.com',         '778-555-0128', '7031 Westminster Hwy, Richmond'),
('P029', 'Ahmed Farouk',     'ahmed.farouk@outlook.com',     '604-555-0129', '1023 Davie St, Vancouver'),
('P030', 'Clara Fontaine',   'clara.fontaine@gmail.com',     '778-555-0130', '4295 Main St, Vancouver');

-- ==== Member (12 rows; P001-P010 are Person A's borrowers, so they must be here) ====
INSERT INTO Member (personID, membershipDate, membershipStatus) VALUES
('P001', '2023-01-15', 'Active'),
('P002', '2022-06-03', 'Active'),
('P003', '2023-09-27', 'Active'),
('P004', '2024-02-11', 'Active'),
('P005', '2021-11-30', 'Active'),
('P006', '2022-08-19', 'Expired'),
('P007', '2024-05-02', 'Active'),
('P008', '2023-03-14', 'Active'),
('P009', '2020-10-07', 'Expired'),
('P010', '2024-07-21', 'Suspended'),
('P011', '2025-01-09', 'Active'),
('P012', '2023-12-01', 'Active');

-- ==== Staff (10 rows; P013 is the head of the library, so no supervisor) ====
INSERT INTO Staff (personID, role, hireDate, salary, supervisorID) VALUES
('P013', 'Head Librarian',      '2015-04-01', 88000.00, NULL),
('P014', 'Senior Librarian',    '2017-09-15', 71000.00, 'P013'),
('P018', 'IT Specialist',       '2018-03-12', 68000.00, 'P013'),
('P015', 'Librarian',           '2019-06-01', 63000.00, 'P014'),
('P019', 'Archivist',           '2019-10-05', 58000.00, 'P014'),
('P017', 'Events Coordinator',  '2020-01-20', 54000.00, 'P013'),
('P020', 'Librarian',           '2021-02-10', 61500.00, 'P014'),
('P016', 'Library Technician',  '2021-11-01', 52000.00, 'P015'),
('P027', 'Reference Librarian', '2022-08-22', 60000.00, 'P014'),
('P002', 'Circulation Clerk',   '2023-05-08', 47500.00, 'P015');

-- ==== Volunteer (10 rows) ====
INSERT INTO Volunteer (personID, startDate, hoursLogged) VALUES
('P021', '2022-04-18', 310.5),
('P022', '2023-02-06', 185.0),
('P005', '2023-07-12', 122.5),
('P023', '2023-10-23', 96.0),
('P016', '2024-01-15', 74.5),
('P024', '2024-03-30', 58.0),
('P012', '2024-09-08', 41.5),
('P028', '2025-02-14', 27.0),
('P029', '2025-06-19', 12.5),
('P030', '2026-07-28', 0.0);

-- ==== Room (10 rows) ====
INSERT INTO Room (roomID, name, capacity) VALUES
('R001', 'Main Hall',        120),
('R002', 'Community Room',    60),
('R003', 'Meeting Room A',    20),
('R004', 'Meeting Room B',    20),
('R005', 'Childrens Corner',  25),
('R006', 'Media Lab',         16),
('R007', 'Quiet Study Room',  12),
('R008', 'Seminar Room',      30),
('R009', 'Gallery Space',     45),
('R010', 'Tutoring Pod',       4);

-- ==== Event (12 rows; E003/E012 share R001 on 2026-08-14 without overlapping,
--      E008 has a NULL description, E011 fills its room to capacity below) ====
INSERT INTO Event (eventID, title, description, eventType, eventDate, startTime, endTime, roomID) VALUES
('E001', 'Summer Mystery Book Club',      'Discussing "Silent Rivers" by M. Alvarez over coffee.', 'BookClub',      '2026-08-12', '18:00', '19:30', 'R003'),
('E002', 'Watercolour Art Show',          'Local artists exhibit; artists in attendance 1-3pm.',   'ArtShow',       '2026-08-15', '10:00', '16:00', 'R009'),
('E003', 'Classic Film Night: Metropolis','1927 restoration with live piano accompaniment.',       'FilmScreening', '2026-08-14', '19:00', '21:30', 'R001'),
('E004', 'Teen Graphic Novel Club',       'This month: manga classics. Snacks provided.',          'BookClub',      '2026-08-19', '16:00', '17:00', 'R004'),
('E005', 'Local History Talk',            'The neighbourhood before the library: photos and maps.','Other',         '2026-08-20', '14:00', '15:30', 'R008'),
('E006', 'Kids Storytime Hour',           'Picture books and songs for ages 3-6.',                 'Other',         '2026-08-08', '10:30', '11:30', 'R005'),
('E007', 'Documentary Screening: Oceans', 'Followed by a short Q&A with a marine biologist.',      'FilmScreening', '2026-08-21', '18:30', '20:00', 'R006'),
('E008', 'Poetry Open Mic',               NULL,                                                    'Other',         '2026-08-22', '19:00', '21:00', 'R002'),
('E009', 'Seniors Tech Help Drop-in',     'One-on-one help with phones, tablets, and e-books.',    'Other',         '2026-08-25', '13:00', '15:00', 'R006'),
('E010', 'Fall Reading Kickoff',          'Launch of the fall reading challenge; sign-ups open.',  'BookClub',      '2026-09-02', '18:00', '19:00', 'R002'),
('E011', 'One-on-One Tutoring Demo',      'Meet our volunteer tutors; very limited seating.',      'Other',         '2026-08-18', '15:00', '16:00', 'R010'),
('E012', 'Indie Film Shorts Evening',     'Six short films from BC filmmakers.',                   'FilmScreening', '2026-08-14', '15:00', '17:00', 'R001');

-- ==== AudienceGroup (all 5 rows) ====
-- README §1 fixes this entity set to exactly five groups (Kids/Teens/Adults/Seniors/AllAges),
-- and the CHECK enforces it, so 10 rows are impossible here: the full domain is 5 rows.
INSERT INTO AudienceGroup (groupName) VALUES
('Kids'),
('Teens'),
('Adults'),
('Seniors'),
('AllAges');

-- ==== RecommendedFor (14 rows) ====
INSERT INTO RecommendedFor (eventID, groupName) VALUES
('E001', 'Adults'),
('E001', 'Seniors'),
('E002', 'AllAges'),
('E003', 'Adults'),
('E004', 'Teens'),
('E005', 'Adults'),
('E005', 'Seniors'),
('E006', 'Kids'),
('E007', 'Teens'),
('E007', 'Adults'),
('E008', 'AllAges'),
('E009', 'Seniors'),
('E010', 'Adults'),
('E011', 'Teens');

-- ==== Attends (17 rows) ====
-- E011 is at its room's capacity (4 of 4 in the Tutoring Pod) — a 5th registration trips
-- the Attends_Capacity trigger. P025 and P026 attending shows people in no subclass
-- still interact with the library (partial isa).
INSERT INTO Attends (personID, eventID, registrationDate) VALUES
('P001', 'E001', '2026-07-30'),
('P003', 'E001', '2026-08-01'),
('P004', 'E001', '2026-08-03'),
('P009', 'E002', '2026-08-02'),
('P002', 'E003', '2026-07-28'),
('P006', 'E003', '2026-08-01'),
('P025', 'E003', '2026-08-04'),
('P026', 'E003', '2026-08-05'),
('P011', 'E006', '2026-08-02'),
('P007', 'E008', '2026-08-03'),
('P008', 'E008', '2026-08-05'),
('P010', 'E010', '2026-08-01'),
('P028', 'E010', '2026-08-04'),
('P001', 'E011', '2026-07-29'),
('P005', 'E011', '2026-07-31'),
('P012', 'E011', '2026-08-02'),
('P026', 'E011', '2026-08-03');
