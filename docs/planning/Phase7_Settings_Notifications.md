# Phase 7: System Configuration & Notifications

## 1. Overview
**Goal:** Reduce reliance on hardcoded values and improve communication.

## 2. Features

### Library Settings (Singleton Model)
*   **Model:** `LibraryConfiguration`
    *   `fine_per_day`: Decimal
    *   `max_renewals`: Integer
    *   `hold_expiry_days`: Integer (How long a reserved book waits on the shelf).
*   **UI:** Admin form to update these values.

### Fine Management
*   **Workflow:** "Pay Fine" button in Member Detail view (Librarian only).
*   **Logic:** Reduces `BorrowRecord.fine_amount` or creates a `Transaction` record (Credit/Debit).

### Notifications
*   **Triggers:**
    *   Book Issued / Returned.
    *   Reservation Available (CRITICAL).
    *   Overdue Warning (Cron job).
*   **Channels:**
    *   **In-App:** Notification bell in Navbar.
    *   **Email:** Django Email Backend (Console for dev).

## 3. Deliverables
1.  Settings Dashboard.
2.  Transaction/Payment Ledger.
3.  Notification System.
