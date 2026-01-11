# Phase 4: Advanced Features & Reporting

## 1. Overview
**Goal:** Enhance the system with analytics, user engagement features (reviews), and AI support.

## 2. Technical Implementation

### 2.1 Analytics Module (`analytics` app)
*   **Dashboard:** System-wide overview for Librarians.
*   **Metrics:** Total borrows (monthly), total fines collected, active overdue counts, and lost book tracking.
*   **Insights:** Most popular books based on borrow frequency.

### 2.2 Lost Book Handling
*   **Workflow:** Integration into the "Return Book" interface.
*   **Logic:** Marking a book as lost automatically updates the record status and applies a replacement fine (Book Price + Processing Fee).
*   **Stock:** Lost books are removed from active circulation.

### 2.3 Reviews & Ratings (`books` app)
*   **Logic:** Members who have returned a book can leave a 1-5 star rating and text review.
*   **UI:** average ratings displayed on book cards and detail pages. Recent reviews list on the detail page.

### 2.4 AI Chatbot Integration
*   **Implementation:** Floating widget on the frontend communicating with a custom intent-based API.
*   **Capabilities:**
    *   Availability checks ("Is [Title] available?").
    *   Personal loan status ("When is my book due?").
    *   Recommendations ("Can you recommend a book?").

### 2.5 Custom Report Builder (Enhancement)
*   **Goal:** Provide flexible, downloadable reports for Librarians.
*   **Filters:** Date Range, Report Type (Borrowing, Overdue, Fines).
*   **Output:** Dynamic table view with Print/PDF capability.

## 3. Deliverables (COMPLETED)
1.  [x] `analytics` app created.
2.  [x] Librarian Analytics Dashboard implemented.
3.  [x] "Mark as Lost" button and logic added to Return flow.
4.  [x] Review system (Model + Form + Display) implemented.
5.  [x] AI Chatbot widget and backend intent handler implemented.
6.  [x] Live Status Summary added to the main User Dashboard.
7.  [x] Custom Report Builder implemented (`/analytics/reports/`).

## 4. Verification Checklist
*   [x] Verify Analytics dashboard displays correct counts.
*   [x] Verify "Lost" button correctly applies book price as a fine.
*   [x] Verify Members can submit reviews only after returning a book.
*   [x] Test Chatbot for basic availability and due date queries.