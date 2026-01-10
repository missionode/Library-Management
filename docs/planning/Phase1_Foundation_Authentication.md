# Phase 1: Foundation & Authentication

## 1. Overview
**Goal:** Establish the Django project structure, configure the database, and implement a secure, role-based authentication system. This phase lays the groundwork for all subsequent modules.

## 2. Technical Requirements

### 2.1 Project Setup
*   **Framework:** Django 6.x
*   **Database:** SQLite (Development) -> PostgreSQL (Production ready)
*   **Styling:** **Tailwind CSS** (via CDN for dev) for modern, utility-first design.

### 2.2 Database Models

#### `User` (Custom Model inheriting `AbstractUser`)
*   **Fields:**
    *   `username`, `password`, `email` (Standard Django fields)
    *   `role`: Enum/Choices [`ADMIN`, `LIBRARIAN`, `MEMBER`]
    *   `phone_number`: CharField
    *   `address`: TextField
    *   `profile_image`: ImageField (Optional)
    *   `created_at`: DateTime

### 2.3 Features & Functionality

#### Authentication System
*   **Registration:** Public registration page for `MEMBER` role only.
*   **Login:** Unified login page.
*   **Logout:** Secure session termination.

#### Development Credentials Management
*   **File:** `dev_secrets.json` (Local only, not committed).
*   **Script:** `scripts/init_dev_data.py` to auto-populate the database.
*   **Contents:**
    *   Pre-generated Superuser (Admin) credentials.
    *   Pre-generated Librarian credentials.
    *   Test Member credentials.
    *   Django `SECRET_KEY` (for dev environment).
    *   API keys placeholders.

#### Base UI Structure
*   **`base.html`:** Main layout template containing:
    *   **Navbar:** Responsive Tailwind navbar with dynamic links based on auth status.
    *   **Footer:** Standard footer.
    *   **Tailwind Config:** Setup via CDN.

## 3. Deliverables (COMPLETED)
1.  [x] Django project initialized (`library_system`).
2.  [x] `accounts` app created with Custom User Model.
3.  [x] `dev_secrets.json` created with initial login details.
4.  [x] `scripts/init_dev_data.py` created and executed.
5.  [x] Working Login/Register/Logout pages styled with Tailwind.
6.  [x] Basic "Home" landing page.

## 4. Verification Checklist
*   [x] `python manage.py runserver` runs without errors.
*   [x] Admin can log in at `/admin/` and via the custom login page.
*   [x] New user can register as a "Member".
*   [x] Database contains the seed data from `dev_secrets.json`.