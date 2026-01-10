from django.db import models
from django.urls import reverse
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Author(models.Model):
    name = models.CharField(max_length=200)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    STATUS_CHOICES = [
        ('AVAILABLE', 'Available'),
        ('OUT_OF_STOCK', 'Out of Stock'),
        ('RESERVED', 'Reserved'),
    ]

    title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, help_text="13 Character ISBN")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    publication_date = models.DateField()
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Replacement cost of the book")
    cover_image = models.ImageField(upload_to='books/covers/', blank=True, null=True)
    borrow_duration = models.PositiveIntegerField(default=14, help_text="Default borrow duration in days")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AVAILABLE')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status != 'RESERVED':
            if self.available_copies == 0:
                self.status = 'OUT_OF_STOCK'
            else:
                self.status = 'AVAILABLE'
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('book_detail', args=[str(self.id)])

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveSmallIntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book')

    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title}"