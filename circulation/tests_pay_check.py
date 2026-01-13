from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from circulation.models import BorrowRecord
from books.models import Book, Author
from core.models import LibraryConfiguration, Notification

User = get_user_model()

class PayCheckFeatureTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # 1. Setup Librarian
        self.librarian = User.objects.create_user(
            username='librarian', 
            password='password123',
            role=User.Role.LIBRARIAN
        )
        self.client.login(username='librarian', password='password123')

        # 2. Setup Member
        self.member = User.objects.create_user(
            username='member',
            password='password123',
            role=User.Role.MEMBER
        )

        # 3. Setup Author and Book
        self.author = Author.objects.create(name='Test Author')
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            author=self.author,
            publication_date=timezone.now().date(),
            available_copies=1,
            price=Decimal('100.00')
        )

        # 4. Setup Config (Fine = 5.00 per day)
        self.config = LibraryConfiguration.objects.create(fine_per_day=Decimal('5.00'))

    def test_return_clears_notifications(self):
        """Test that returning a book clears related overdue notifications."""
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            status='ISSUED'
        )
        # Force overdue
        record.issued_date = timezone.now() - timedelta(days=20)
        record.due_date = timezone.now() - timedelta(days=2)
        record.save()

        # Create a notification
        notification = Notification.objects.create(
            user=self.member,
            message=f"OVERDUE ALERT: '{self.book.title}' is overdue.",
            is_read=False
        )

        # Return the book
        self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return_pay_now'
        })

        notification.refresh_from_db()
        self.assertTrue(notification.is_read, "Notification should be marked as read after return.")

    def test_return_no_fine(self):
        """Test returning a book on time (no fine)."""
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            issued_date=timezone.now() - timedelta(days=5),
            due_date=timezone.now() + timedelta(days=5), # Not overdue
            status='ISSUED'
        )
        
        response = self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return'
        })
        
        # Should redirect to return_book with username param
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.status, 'RETURNED')
        self.assertEqual(record.fine_amount, Decimal('0.00'))

    def test_return_overdue_confirmation(self):
        """Test that returning an overdue book triggers the confirmation page."""
        overdue_days = 2
        # Create record first (will get default due_date)
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            status='ISSUED'
        )
        # Manually override due_date to force overdue
        record.issued_date = timezone.now() - timedelta(days=20)
        record.due_date = timezone.now() - timedelta(days=overdue_days)
        record.save()

        response = self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return'
        })

        # Should render the confirmation template
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'circulation/fine_confirmation.html')
        
        # Verify context data
        expected_fine = overdue_days * self.config.fine_per_day
        self.assertEqual(response.context['fine_amount'], expected_fine)
        self.assertEqual(response.context['overdue_days'], overdue_days)
        
        # Record should NOT be returned yet
        record.refresh_from_db()
        self.assertEqual(record.status, 'ISSUED')

    def test_return_pay_now(self):
        """Test 'Pay Now' action clears the fine."""
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            status='ISSUED'
        )
        # Override to ensure overdue
        record.issued_date = timezone.now() - timedelta(days=20)
        record.due_date = timezone.now() - timedelta(days=2)
        record.save()

        response = self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return_pay_now'
        })

        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.status, 'RETURNED')
        self.assertEqual(record.fine_amount, Decimal('0.00')) # Cleared

    def test_return_pay_later(self):
        """Test 'Pay Later' action keeps the fine."""
        overdue_days = 2
        record = BorrowRecord.objects.create(
            user=self.member,
            book=self.book,
            status='ISSUED'
        )
        # Override to ensure overdue
        record.issued_date = timezone.now() - timedelta(days=20)
        record.due_date = timezone.now() - timedelta(days=overdue_days)
        record.save()

        response = self.client.post(reverse('return_book'), {
            'record_id': record.id,
            'action': 'return_pay_later'
        })

        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.status, 'RETURNED')
        
        expected_fine = overdue_days * self.config.fine_per_day
        self.assertEqual(record.fine_amount, expected_fine) # Kept
