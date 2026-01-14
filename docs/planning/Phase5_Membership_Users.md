# Phase 5: Membership & User Administration - ✅ COMPLETED

## 1. Overview
**Goal:** Empower Librarians to manage the member base directly and introduce a "Subscription" model to monetize or categorize access (e.g., Basic vs Premium).

## 2. Database Models

#### `MembershipTier`
*   `name`: CharField (e.g., "Basic", "Premium", "Student")
*   `max_books`: IntegerField (Limit on concurrent borrows)
*   `borrow_duration_days`: IntegerField (Overrides book default if set, or acts as a multiplier)
*   `max_renewals`: IntegerField (Limits how many times a single loan can be extended)
*   `subscription_fee`: DecimalField
*   `is_active`: BooleanField

#### `User` (Update)
*   `membership_tier`: ForeignKey -> `MembershipTier`
*   `is_active_member`: BooleanField (For soft banning/blocking)

## 3. Features

### Staff Management (Admin Only) - *Added*
*   **Create Librarian:** Dedicated workflow for Admins to onboard new Librarians (`/accounts/librarian/create/`).
*   **Role Visibility:**
    *   **Admins:** See all users (Members + Librarians).
    *   **Librarians:** See only Members (restricted view).

### Librarian User Management
*   **Member List View:** Searchable table of all users with role 'MEMBER'.
*   **Member Detail View:** Dedicated page (`/accounts/members/<pk>/`) showing profile, borrow history, and fines. Accessible by clicking usernames in the list.
*   **Actions:**
    *   **Block/Unblock:** Toggle `is_active_member`.
    *   **Change Tier:** Manually upgrade/downgrade a user.
    *   **Reset Password:** (Optional, or send reset link).

### Subscription Logic
*   **Enforcement:** Update `IssueBookForm` to check:
    *   Is user active?
    *   `active_loans_count` < `user.membership_tier.max_books`?
*   **Renewals:** Check `current_renewals` < `user.membership_tier.max_renewals` before allowing extension.
*   **Registration:** Update Registration form to select a Tier (or default to Free).

## 4. Deliverables
1.  `MembershipTier` model and fixtures.
2.  Librarian "Member Management" Dashboard.
3.  Updated Issue Logic to respect limits.
