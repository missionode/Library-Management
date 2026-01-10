from django import forms
from django.contrib.auth import get_user_model
from .models import BorrowRecord
from books.models import Book

User = get_user_model()

class IssueBookForm(forms.Form):
    username = forms.CharField(label="Member Username", help_text="Enter the username of the member.")
    book_isbn = forms.CharField(label="Book ISBN", help_text="Scan or enter the Book ISBN.")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
            if user.role != 'MEMBER': # Depending on policy, maybe admins can borrow too? Let's restrict to MEMBERS for now.
                # Actually, Librarians/Admins might borrow too. Let's allow any valid user.
                pass
        except User.DoesNotExist:
            raise forms.ValidationError("User with this username does not exist.")
        return username

    def clean_book_isbn(self):
        isbn = self.cleaned_data['book_isbn']
        try:
            Book.objects.get(isbn=isbn)
        except Book.DoesNotExist:
            raise forms.ValidationError("Book with this ISBN not found.")
        return isbn

class ReturnBookForm(forms.Form):
    book_isbn = forms.CharField(label="Book ISBN", help_text="Scan or enter the Book ISBN.")
    username = forms.CharField(label="Member Username (Optional)", required=False, help_text="If provided, narrows down the search.")
