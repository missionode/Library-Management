from django.contrib.auth.models import AbstractUser
from django.db import models

class MembershipTier(models.Model):
    name = models.CharField(max_length=100)
    max_books = models.PositiveIntegerField(default=2)
    borrow_duration_days = models.PositiveIntegerField(default=14)
    max_renewals = models.PositiveIntegerField(default=1)
    subscription_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        LIBRARIAN = "LIBRARIAN", "Librarian"
        MEMBER = "MEMBER", "Member"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.MEMBER)
    membership_tier = models.ForeignKey(MembershipTier, on_delete=models.SET_NULL, null=True, blank=True)
    is_active_member = models.BooleanField(default=True) # For soft banning
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_superuser:
            self.role = self.Role.ADMIN
        
        # Assign default tier to new members if not set
        if not self.membership_tier and self.role == self.Role.MEMBER:
            basic_tier = MembershipTier.objects.filter(name="Basic").first()
            if basic_tier:
                self.membership_tier = basic_tier
                
        super().save(*args, **kwargs)
