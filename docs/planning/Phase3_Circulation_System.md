# Phase 3: Circulation System (The Core)

## 1. Overview
**Goal:** Manage the lifecycle of a book loan. This is the most complex phase, handling business logic for borrowing, returning, calculating fines, and managing reservations.

## 2. Database Models

#### `BorrowRecord`
*   `user`: ForeignKey -> `User`
*   `book`: ForeignKey -> `Book`
*   `issued_date`: DateTime (Auto Now)
*   `due_date`: DateTime (Calculated based on Book's `borrow_duration`)
*   `return_date`: DateTime (Null initially)
*   `status`: Choices [`ISSUED`, `RETURNED`, `LOST`, `OVERDUE`]
*   `fine_amount`: DecimalField (Default 0.00)

#### `Reservation`
*   `user`: ForeignKey -> `User`
*   `book`: ForeignKey -> `Book`
*   `reserved_date`: DateTime
*   `status`: Choices [`PENDING`, `FULFILLED`, `CANCELLED`]

#### `LibraryRule` (Singleton/Config Model)
*   `standard_fine_per_day`: DecimalField
*   `max_books_per_user`: IntegerField

## 3. Features & Logic

### Librarian Actions
*   **Issue Book:**
    *   Input: User ID/Email and Book ISBN.
    *   Validation: Check if User has reached `max_books` limit. Check if user has unpaid fines. Check if Book `available_copies` > 0.
    *   Action: Create `BorrowRecord`, decrement Book `available_copies`.
*   **Return Book:**
    *   Input: Book ISBN or User ID.
    *   Action: Update `return_date`. Calculate fines if `return_date` > `due_date`. Increment Book `available_copies`. Update Status to `RETURNED`.
    *   **Pay Check Feature:** If a fine is applicable, the Librarian is prompted with a confirmation screen offering "Pay Now" (clears fine immediately) or "Pay Later" (records fine to user account) options.

### Member Actions
*   **Dashboard View:** See list of currently borrowed books with colored status badges (Green: OK, Red: Overdue).
*   **Renew Book:** Option to extend `due_date`.
*   **Reserve Book:** If a book is out of stock, place a reservation.

### Automated Processes (Signals/Cron/Logic)
*   **Fine Calculation:** Logic to check `due_date` vs current date/return date.
*   **Overdue Marking:** Daily check to mark records as `OVERDUE`.
*   **Notification Cleanup:** Automated logic clears "Overdue" notifications from the database when a book is returned or renewed, preventing stale alerts in the user's history.

## 4. Deliverables
1.  `circulation` app created.
2.  Issue/Return interface for Librarians.
3.  Member Dashboard "My Books" section.
4.  Fine calculation logic implementation.
5.  Reservation system.
