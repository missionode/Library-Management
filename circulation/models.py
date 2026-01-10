from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from books.models import Book

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
        ('LOST', 'Lost'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records')
    issued_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ISSUED')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    renewal_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set due date based on book's borrow duration
            self.due_date = timezone.now() + timedelta(days=self.book.borrow_duration)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == 'ISSUED':
            return timezone.now() > self.due_date
        return False

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"

class Reservation(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations')
    reserved_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Reservation: {self.user.username} for {self.book.title}"