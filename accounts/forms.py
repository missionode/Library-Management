from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class MemberRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone_number', 'address')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.MEMBER  # Enforce Member role for public registration
        if commit:
            user.save()
        return user
