# Phase 2: Book Inventory & Management

## 1. Overview
**Goal:** Implement the core cataloging features. This phase enables Librarians to manage the library's physical inventory and allows all users to search and view book details.

## 2. Technical Implementation

### 2.1 Database Models (`books` app)

#### `Category`
*   `name`: CharField
*   `description`: TextField

#### `Author`
*   `name`: CharField
*   `bio`: TextField

#### `Book`
*   `title`: CharField
*   `isbn`: CharField (Unique)
*   `author`: ForeignKey -> `Author`
*   `category`: ForeignKey -> `Category`
*   `publication_date`: DateField
*   `total_copies`: IntegerField
*   `available_copies`: IntegerField
*   `cover_image`: ImageField
*   `borrow_duration`: IntegerField
*   `status`: Choices [`AVAILABLE`, `OUT_OF_STOCK`]

### 2.2 Features & User Stories

#### Librarian / Admin Features
*   **Add Book:** Dedicated form with helper links to add new Authors and Categories on the fly.
*   **Edit/Delete Book:** Management controls available on Book Detail page.
*   **Dashboard Integration:** Quick actions added to the Librarian's Home Dashboard.

#### Member Features
*   **Search Catalog:** Search bar filtering by Title, Author, Category, or ISBN.
*   **Book Details:** View Synopsis, Availability, and Shelf Location info.
*   **Browse:** Responsive grid view of all books.

## 3. Deliverables (COMPLETED)
1.  [x] `books` app created and registered.
2.  [x] Database models (Book, Author, Category) created and migrated.
3.  [x] Librarian views: Create, Update, Delete for Books, Authors, and Categories.
4.  [x] Public views: Book List (Searchable) and Book Detail.
5.  [x] Templates styled with Tailwind CSS.
6.  [x] Navigation updated with "Browse Books" and Librarian "Quick Actions".
7.  [x] Media files configuration fixed for serving cover images.

## 4. Verification Checklist
*   [x] Access `/books/` to see the catalog.
*   [x] Login as Librarian to see "Add New Book" button on Dashboard.
*   [x] Successfully add a new Author and Category via the Add Book form.
*   [x] Upload a cover image and verify it displays on the list and detail pages.
*   [x] Verify Search functionality works for titles and authors.