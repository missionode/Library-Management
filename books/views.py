from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q
from .models import Book, Author, Category
from .forms import BookForm, AuthorForm, CategoryForm

# Mixin to restrict access to Librarians and Admins
class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['LIBRARIAN', 'ADMIN']

# Public Views
class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 12

    def get_queryset(self):
        query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        user = self.request.user
        
        queryset = Book.objects.all().order_by('-publication_date')
        
        # Hide LOST books from non-staff
        if not (user.is_authenticated and user.role in ['LIBRARIAN', 'ADMIN']):
            queryset = queryset.exclude(status='LOST')
        
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(author__name__icontains=query) |
                Q(category__name__icontains=query) |
                Q(isbn__icontains=query)
            )
            
        if status_filter:
            if status_filter == 'available':
                queryset = queryset.filter(status='AVAILABLE')
            elif status_filter == 'borrowed':
                queryset = queryset.filter(status__in=['OUT_OF_STOCK', 'RESERVED'])
            elif status_filter == 'lost' and user.is_authenticated and user.role in ['LIBRARIAN', 'ADMIN']:
                queryset = queryset.filter(status='LOST')
                
        return queryset

from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Q, Avg
from .models import Book, Author, Category, Review
from circulation.models import BorrowRecord
from .forms import BookForm, AuthorForm, CategoryForm

# ... (Mixins and List views remain same)

class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.get_object()
        
        # Calculate Avg Rating
        context['avg_rating'] = book.reviews.aggregate(Avg('rating'))['rating__avg']
        
        # Check if current user can review (must have borrowed and returned this book)
        if self.request.user.is_authenticated:
            context['can_review'] = BorrowRecord.objects.filter(
                user=self.request.user,
                book=book,
                status='RETURNED'
            ).exists() and not Review.objects.filter(user=self.request.user, book=book).exists()
            
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        book = self.get_object()
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating and comment:
            Review.objects.create(
                user=request.user,
                book=book,
                rating=rating,
                comment=comment
            )
        
        return redirect('book_detail', pk=book.pk)

# Librarian Views - Books
class BookCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

class BookUpdateView(LoginRequiredMixin, LibrarianRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('book_list')

from django.contrib import messages

class BookDeleteView(LoginRequiredMixin, LibrarianRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')

    def delete(self, request, *args, **kwargs):
        book = self.get_object()
        active_loans = BorrowRecord.objects.filter(book=book, status='ISSUED').exists()
        
        if active_loans:
            messages.error(request, f"Cannot delete '{book.title}' because copies are currently issued. Please adjust the total copies instead.")
            return redirect('book_edit', pk=book.pk)
            
        return super().delete(request, *args, **kwargs)

# Librarian Views - Authors
class AuthorCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = Author
    form_class = AuthorForm
    template_name = 'books/author_form.html'
    success_url = reverse_lazy('book_add') # Redirect back to book add usually, or list

# Librarian Views - Categories
class CategoryCreateView(LoginRequiredMixin, LibrarianRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'books/category_form.html'
    success_url = reverse_lazy('book_add')
