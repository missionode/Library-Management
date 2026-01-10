from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from books.models import Book, Author, Category
from circulation.models import BorrowRecord, Reservation
from accounts.models import MembershipTier

User = get_user_model()

class CirculationTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Setup Tier
        self.tier = MembershipTier.objects.create(
            name="Premium",
            max_books=5,
            borrow_duration_days=14,
            max_renewals=1
        )
        
        # Setup Users
        self.member = User.objects.create_user(username='member', password='password', role='MEMBER', membership_tier=self.tier)
        self.librarian = User.objects.create_user(username='librarian', password='password', role='LIBRARIAN')
        self.other_member = User.objects.create_user(username='other', password='password', role='MEMBER', membership_tier=self.tier)

        # Setup Book
        self.author = Author.objects.create(name="Test Author")
        self.book = Book.objects.create(
            title="Test Book",
            isbn="1234567890123",
            author=self.author,
            publication_date="2023-01-01",
            total_copies=1,
            available_copies=0, # Out of stock initially for some tests
            borrow_duration=14,
            price=10.00
        )
        self.book.save() # Triggers status update

    def test_renew_book_success(self):
        self.client.login(username='member', password='password')
        
        # Issue book
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14),
            status='ISSUED'
        )
        
        response = self.client.post(reverse('renew_book', args=[record.pk]))
        self.assertEqual(response.status_code, 302) # Redirects
        
        record.refresh_from_db()
        self.assertEqual(record.renewal_count, 1)
        # Due date should be extended (approximate check)
        self.assertTrue(record.due_date > timezone.now() + timedelta(days=14))

    def test_renew_book_limit_reached(self):
        self.client.login(username='member', password='password')
        
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14),
            status='ISSUED',
            renewal_count=1 # Limit is 1
        )
        
        response = self.client.post(reverse('renew_book', args=[record.pk]))
        # Should fail and redirect
        record.refresh_from_db()
        self.assertEqual(record.renewal_count, 1) # Not incremented

    def test_renew_book_blocked_by_reservation(self):
        self.client.login(username='member', password='password')
        
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14),
            status='ISSUED'
        )
        
        # Create reservation by another user
        Reservation.objects.create(user=self.other_member, book=self.book)
        
        response = self.client.post(reverse('renew_book', args=[record.pk]))
        
        record.refresh_from_db()
        self.assertEqual(record.renewal_count, 0) # Blocked

    def test_reserve_book_success(self):
        self.client.login(username='member', password='password')
        self.book.available_copies = 0
        self.book.status = 'OUT_OF_STOCK'
        self.book.save()
        
        response = self.client.post(reverse('reserve_book', args=[self.book.pk]))
        self.assertEqual(response.status_code, 302)
        
        self.assertTrue(Reservation.objects.filter(user=self.member, book=self.book).exists())

    def test_reserve_book_fail_if_available(self):
        self.client.login(username='member', password='password')
        self.book.available_copies = 1
        self.book.save() # Should set status AVAILABLE
        
        response = self.client.post(reverse('reserve_book', args=[self.book.pk]))
        
        self.assertFalse(Reservation.objects.filter(user=self.member, book=self.book).exists())

    def test_return_book_handles_reservation(self):
        self.client.login(username='librarian', password='password')
        
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            due_date=timezone.now() + timedelta(days=14),
            status='ISSUED'
        )
        
        # Reservation exists
        Reservation.objects.create(user=self.other_member, book=self.book)
        
        response = self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return'
        })
        
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 'RESERVED')
        # available_copies should NOT increment (stays 0)
        self.assertEqual(self.book.available_copies, 0) 

    def test_issue_reserved_book_success(self):
        self.client.login(username='librarian', password='password')
        
        # Setup: Book is reserved for member
        self.book.status = 'RESERVED'
        self.book.available_copies = 0
        self.book.save()
        Reservation.objects.create(user=self.member, book=self.book)
        
        response = self.client.post(reverse('issue_book'), {
            'username': 'member',
            'book_isbn': self.book.isbn
        })
        
        self.assertRedirects(response, reverse('issue_book'))
        
        # Check BorrowRecord created
        self.assertTrue(BorrowRecord.objects.filter(user=self.member, book=self.book, status='ISSUED').exists())
        
        # Check Reservation fulfilled
        self.assertEqual(Reservation.objects.get(user=self.member, book=self.book).status, 'FULFILLED')
        
        # Check Book status
        self.book.refresh_from_db()
        self.assertEqual(self.book.status, 'OUT_OF_STOCK') # Still 0 copies

    def test_issue_reserved_book_wrong_user(self):
        self.client.login(username='librarian', password='password')
        
        # Setup: Book is reserved for member
        self.book.status = 'RESERVED'
        self.book.available_copies = 0
        self.book.save()
        Reservation.objects.create(user=self.member, book=self.book)
        
        # Try to issue to other_member
        response = self.client.post(reverse('issue_book'), {
            'username': 'other',
            'book_isbn': self.book.isbn
        })
        
        # Should show error (stay on page)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This book is reserved for member.")
        
        # Check NO BorrowRecord created
        self.assertFalse(BorrowRecord.objects.filter(user=self.other_member, book=self.book, status='ISSUED').exists())