import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import MembershipTier
from books.models import Author, Category, Book, Review
from circulation.models import BorrowRecord, Reservation
from core.models import Notification, LibraryConfiguration

User = get_user_model()

def create_membership_tiers():
    print("Creating Membership Tiers...")
    MembershipTier.objects.all().delete()
    
    basic = MembershipTier.objects.create(
        name="Basic",
        max_books=2,
        borrow_duration_days=14,
        max_renewals=1,
        subscription_fee=0.00
    )
    premium = MembershipTier.objects.create(
        name="Premium",
        max_books=5,
        borrow_duration_days=30,
        max_renewals=3,
        subscription_fee=10.00
    )
    return basic, premium

def create_users(basic_tier, premium_tier):
    print("Creating Users...")
    User.objects.exclude(is_superuser=True).delete()

    # Admin (if not exists)
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')

    # Librarian
    librarian = User.objects.create_user('librarian', 'lib@example.com', 'librarian123', role='LIBRARIAN')
    
    # Members
    john = User.objects.create_user('member_john', 'john@example.com', 'password123', role='MEMBER', membership_tier=basic_tier)
    jane = User.objects.create_user('member_jane', 'jane@example.com', 'password123', role='MEMBER', membership_tier=premium_tier)
    bob = User.objects.create_user('member_bob', 'bob@example.com', 'password123', role='MEMBER', membership_tier=basic_tier)

    return librarian, john, jane, bob

def create_books():
    print("Creating Books...")
    Author.objects.all().delete()
    Category.objects.all().delete()
    Book.objects.all().delete()

    # Authors
    authors = [
        Author.objects.create(name="J.K. Rowling"),
        Author.objects.create(name="George Orwell"),
        Author.objects.create(name="J.R.R. Tolkien"),
        Author.objects.create(name="Isaac Asimov"),
        Author.objects.create(name="Agatha Christie"),
    ]

    # Categories
    categories = [
        Category.objects.create(name="Fantasy"),
        Category.objects.create(name="Sci-Fi"),
        Category.objects.create(name="Mystery"),
        Category.objects.create(name="Classic"),
        Category.objects.create(name="Dystopian"),
    ]

    # Books
    books_data = [
        ("Harry Potter and the Philosopher's Stone", authors[0], categories[0], 5),
        ("1984", authors[1], categories[4], 3),
        ("The Hobbit", authors[2], categories[0], 2),
        ("Foundation", authors[3], categories[1], 4),
        ("Murder on the Orient Express", authors[4], categories[2], 3),
        ("Animal Farm", authors[1], categories[4], 2),
        ("The Fellowship of the Ring", authors[2], categories[0], 0), # Out of stock
        ("I, Robot", authors[3], categories[1], 1),
    ]

    books = []
    for title, author, category, copies in books_data:
        book = Book.objects.create(
            title=title,
            isbn=f"978-{random.randint(100000000, 999999999)}",
            author=author,
            category=category,
            publication_date=timezone.now().date() - timedelta(days=random.randint(365, 3650)),
            total_copies=copies + 2 if copies == 0 else copies, # Ensure total > 0 even if available is 0
            available_copies=copies,
            price=Decimal(random.randint(10, 30)),
            borrow_duration=14
        )
        books.append(book)
    
    return books

def create_circulation(users, books):
    print("Creating Circulation Data...")
    librarian, john, jane, bob = users
    
    # 1. Active Loan (John - Normal)
    BorrowRecord.objects.create(
        user=john,
        book=books[0], # Harry Potter
        issued_date=timezone.now() - timedelta(days=5),
        due_date=timezone.now() + timedelta(days=9),
        status='ISSUED'
    )

    # 2. Overdue Loan (Bob - Fine)
    config = LibraryConfiguration.load()
    overdue_days = 5
    record = BorrowRecord.objects.create(
        user=bob,
        book=books[1], # 1984
        issued_date=timezone.now() - timedelta(days=20),
        due_date=timezone.now() - timedelta(days=overdue_days),
        status='ISSUED'
    )
    # Note: Fine is usually calculated on return, but we can display potential fine
    
    # 3. Returned Book (Jane - History)
    BorrowRecord.objects.create(
        user=jane,
        book=books[3], # Foundation
        issued_date=timezone.now() - timedelta(days=30),
        due_date=timezone.now() - timedelta(days=16),
        return_date=timezone.now() - timedelta(days=18),
        status='RETURNED'
    )

    # 4. Reservation (Jane reserves Out of Stock book)
    out_of_stock_book = books[6] # Fellowship
    Reservation.objects.create(
        user=jane,
        book=out_of_stock_book,
        status='PENDING'
    )

    # 5. Reviews
    Review.objects.create(
        user=jane,
        book=books[3],
        rating=5,
        comment="Absolutely loved it! A masterpiece of sci-fi."
    )

def create_notifications(users):
    print("Creating Notifications...")
    librarian, john, jane, bob = users
    
    Notification.objects.create(user=john, message="Welcome to the library! You have borrowed your first book.")
    Notification.objects.create(user=bob, message="Warning: '1984' is overdue. Please return it to avoid fines.")
    Notification.objects.create(user=jane, message="Your review for 'Foundation' has been posted.")

if __name__ == '__main__':
    basic, premium = create_membership_tiers()
    users = create_users(basic, premium)
    books = create_books()
    create_circulation(users, books)
    create_notifications(users)
    print("Dummy data populated successfully!")
