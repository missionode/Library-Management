import os
import sys
import django
import random
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_system.settings')
django.setup()

from books.models import Book, Author, Category

def add_books():
    # Ensure categories exist
    cats = ['Fiction', 'Science', 'History', 'Technology', 'Fantasy']
    cat_objs = []
    for c in cats:
        obj, _ = Category.objects.get_or_create(name=c)
        cat_objs.append(obj)

    sample_data = [
        ("The Great Gatsby", "F. Scott Fitzgerald", "9780743273565", "Fiction"),
        ("1984", "George Orwell", "9780451524935", "Fiction"),
        ("A Brief History of Time", "Stephen Hawking", "9780553380163", "Science"),
        ("Sapiens", "Yuval Noah Harari", "9780062316097", "History"),
        ("Clean Code", "Robert C. Martin", "9780132350884", "Technology"),
        ("The Hobbit", "J.R.R. Tolkien", "9780547928227", "Fantasy"),
        ("Dune", "Frank Herbert", "9780441013593", "Fantasy"),
        ("Thinking, Fast and Slow", "Daniel Kahneman", "9780374275631", "Science"),
        ("To Kill a Mockingbird", "Harper Lee", "9780061120084", "Fiction"),
        ("Python Crash Course", "Eric Matthes", "9781593279288", "Technology"),
    ]

    count = 0
    for title, author_name, isbn, cat_name in sample_data:
        if not Book.objects.filter(isbn=isbn).exists():
            author, _ = Author.objects.get_or_create(name=author_name)
            category = Category.objects.get(name=cat_name)
            
            Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                category=category,
                publication_date=date(2020, 1, 1),
                total_copies=5,
                available_copies=5,
                price=19.99,
                borrow_duration=14
            )
            print(f"Added: {title}")
            count += 1
        else:
            print(f"Skipped: {title} (Exists)")

    print(f"\nSuccessfully added {count} books.")

if __name__ == '__main__':
    add_books()
