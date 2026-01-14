from django import forms
from .models import Book, Author, Category

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'isbn', 'author', 'category', 'publication_date', 
                  'total_copies', 'available_copies', 'price', 'cover_image', 'borrow_duration']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_total_copies(self):
        copies = self.cleaned_data['total_copies']
        if copies < 1:
            raise forms.ValidationError("Total copies must be at least 1.")
        return copies

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.pk:
            instance.available_copies = instance.total_copies
        if commit:
            instance.save()
        return instance

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']