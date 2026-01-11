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

class LibrarianCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.LIBRARIAN
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'address', 'profile_image')
