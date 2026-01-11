# Library Management System - Master Project Plan (Updated)

## Executive Summary
This document outlines the architectural roadmap for the Library Management System. Phases 1-4 provided a functional core. Phases 5-7 are now added to address advanced workflows, subscription management, and system configuration.

---

## Phase Breakdown

### [Phase 1: Foundation & Authentication](./Phase1_Foundation_Authentication.md) - ✅ COMPLETED
*   Project initialization, Custom User Model, Security, and Auth Views.

### [Phase 2: Book Inventory & Management](./Phase2_Book_Management.md) - ✅ COMPLETED
*   Catalog management (Books, Authors, Categories), Public Search, and Media handling.

### [Phase 3: Circulation System](./Phase3_Circulation_System.md) - ✅ COMPLETED
*   Issue/Return workflows, Fine calculation, Barcode Scanner, and "My Books" dashboard.

### [Phase 4: Advanced Features & Reporting](./Phase4_Advanced_Features.md) - ✅ COMPLETED
*   Analytics Dashboard, Lost Book logic, Reviews/Ratings, and AI Chatbot.

### [Phase 5: Membership & User Administration](./Phase5_Membership_Users.md) - ✅ COMPLETED
*   **Goal:** Enable Librarians to manage users and implement subscription tiers.
*   **Features:**
    *   `MembershipTier` model (Name, Max Books, Duration, Fee).
    *   Librarian Dashboard: List/Search/Edit Members.
    *   Block/Unblock functionality.
    *   Enforce borrow limits based on Tier.

### [Phase 6: Advanced Circulation (Renewals & Reservations)](./Phase6_Renewals_Reservations.md) - ✅ COMPLETED
*   **Goal:** Complete the circulation lifecycle with renewals and holds.
*   **Features:**
    *   **Renewal:** Self-service extension of due dates (if eligible).
    *   **Reservations:** Logic to "Hold" a book when all copies are out.
    *   **Return Alert:** Notify Librarian if a returned book is reserved.

### [User Profile Page](./Profile_Page_Update.md) - ✅ COMPLETED
*   **Goal:** Allow users to manage their personal details and profile picture.
*   **Features:** Profile View, Image Upload, Navbar Integration.

### [UI/UX Modernization](./UI_UX_Modernization.md) - ✅ COMPLETED
*   **Goal:** Establish a modern, accessible design language.
*   **Features:** Tailwind v4, Dark Mode, Glassmorphism, Responsive Components.

### [Phase 7: System Configuration & Notifications](./Phase7_Settings_Notifications.md) - ✅ COMPLETED
*   **Goal:** Make the system dynamic and communicative.
*   **Features:**
    *   **Dynamic Settings:** UI to change Fine Amount, Default Duration etc. without code deployment.
    *   **Fine Management:** Workflow to pay off fines.
    *   **Notifications:** Email/In-App alerts for Due Dates and Reservations.

### Additional Enhancements - ✅ COMPLETED
*   **Custom Report Builder:** Advanced filtering and reporting for Library Analytics.
*   **Role-Based Management:** Strict visibility controls for Librarians vs Admins.
*   **Staff Onboarding:** Admin-exclusive "Create Librarian" workflow.

---

## Technical Stack
*   **Backend:** Python 3.12 / Django 6.0
*   **Frontend:** Tailwind CSS v4 (CDN)
*   **Database:** SQLite (Development)
