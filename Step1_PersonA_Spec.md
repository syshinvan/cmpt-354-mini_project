# Step 1: Project Specifications (Person A's portion: Item / Loan / Fine / AcquisitionCandidate)

## Items

The library holds several kinds of items available to patrons: print books, online (e-) books, magazines, journals, and recordings (e.g., CDs, vinyl records, DVDs). Every item, regardless of type, has a title, the method by which it was acquired (purchased or donated), the date it was added to the collection, and a current status (available, checked out, or lost). Print books and online books share details such as ISBN and author, but differ in that a print book has a physical shelf location while an online book has a file format and an access URL instead. Magazines and journals are periodicals: magazines are identified by issue number, publication date, and publisher, while journals are identified by volume, issue number, and subject area. Recordings have an artist, a format, and a duration.

## Borrowing, Returns, and Fines

Members can borrow items from the library. Each time a member borrows an item, this creates a loan with a due date; when the item comes back, a return date is recorded. The same member can borrow the same item more than once over time, so each borrowing is tracked as its own event rather than a single fixed relationship between a member and an item. If a loan is not returned by its due date, it becomes overdue and the library may issue a fine for that specific loan, with an amount owed, the date it was issued, and (once settled) the date it was paid. Not every loan results in a fine; only those returned late or never returned.

## Future Acquisitions

The library also keeps a record of items being considered for future acquisition. Each proposed item has a title, a format, an estimated cost, the date it was proposed, and a status indicating whether the proposal is still pending, has been approved, or was rejected. A proposal may optionally be linked to the person who suggested it, if that information is known. Once approved, an acquisition candidate is expected to eventually become an actual item in the collection, but that transition is handled by library staff rather than being an automatic part of the data itself.
