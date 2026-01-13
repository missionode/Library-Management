from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView, ListView, View
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .forms import IssueBookForm
from .models import BorrowRecord, Reservation
from books.models import Book
from core.models import LibraryConfiguration, Notification

User = get_user_model()

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.role in [User.Role.LIBRARIAN, User.Role.ADMIN]

class IssueBookView(LoginRequiredMixin, LibrarianRequiredMixin, FormView):
    template_name = 'circulation/issue_book.html'
    form_class = IssueBookForm
    success_url = reverse_lazy('issue_book')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        context['issued_today_count'] = BorrowRecord.objects.filter(issued_date__date=today).count()
        context['recent_issues'] = BorrowRecord.objects.select_related('user', 'book').order_by('-issued_date')[:5]
        context['members'] = User.objects.filter(role='MEMBER').values('username', 'first_name', 'last_name')
        context['books'] = Book.objects.all().values('title', 'isbn')
        return context

    def form_valid(self, form):
        # Additional validation logic
        username = form.cleaned_data['username']
        isbn = form.cleaned_data['book_isbn']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            form.add_error('username', 'User not found.')
            return self.form_invalid(form)

        try:
            book = Book.objects.get(isbn=isbn)
        except Book.DoesNotExist:
            form.add_error('book_isbn', 'Book not found.')
            return self.form_invalid(form)

        # Check availability and reservations
        reservation = Reservation.objects.filter(book=book, status='PENDING').order_by('reserved_date').first()
        
        # If reserved for SOMEONE ELSE
        if reservation and reservation.user != user:
             form.add_error('book_isbn', f"This book is reserved for {reservation.user.username}.")
             return self.form_invalid(form)

        if book.available_copies < 1:
            # Allow if reserved for THIS user
            if reservation and reservation.user == user:
                pass # Allow issue
            else:
                form.add_error('book_isbn', 'Book is currently unavailable.')
                return self.form_invalid(form)
            
        # Check active borrow limit
        active_borrows = BorrowRecord.objects.filter(user=user, status='ISSUED').count()
        limit = user.membership_tier.max_books if user.membership_tier else 0
        if active_borrows >= limit:
             form.add_error(None, f"User has reached their borrow limit of {limit} books.")
             return self.form_invalid(form)

        # Create Borrow Record
        BorrowRecord.objects.create(user=user, book=book)
        
        # Handle Stock and Reservation
        if reservation and reservation.user == user:
             reservation.status = 'FULFILLED'
             reservation.save()
             # Stock was already 0 (or effectively reserved), so we don't decrement if it was 0.
             # If it was > 0 but reserved, we decrement.
             if book.available_copies > 0:
                 book.available_copies -= 1
             
             # Reset status to standard logic (OUT_OF_STOCK if 0)
             book.status = 'OUT_OF_STOCK' if book.available_copies == 0 else 'AVAILABLE'
             book.save()
        else:
            book.available_copies -= 1
            book.save()
        
        # Send Notification
        Notification.objects.create(
            user=user,
            message=f"You have successfully borrowed '{book.title}'. Due date: {BorrowRecord.objects.filter(user=user, book=book).last().due_date.strftime('%b %d, %Y')}."
        )

        messages.success(self.request, f"Issued '{book.title}' to {user.username}.")
        return super().form_valid(form)

class RenewBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        record = get_object_or_404(BorrowRecord, pk=pk, user=request.user, status='ISSUED')
        
        # Logic Check
        # 1. Check if book is reserved by someone else
        if Reservation.objects.filter(book=record.book, status='PENDING').exists():
            messages.error(request, f"Cannot renew '{record.book.title}'. It has been reserved by another member.")
            return redirect('my_books')
        
        # 2. Check renewal limit
        max_renewals = request.user.membership_tier.max_renewals if request.user.membership_tier else 1
        if record.renewal_count >= max_renewals:
            messages.error(request, f"Maximum renewal limit ({max_renewals}) reached for '{record.book.title}'.")
            return redirect('my_books')

        # 3. Process Renewal
        days_to_add = 14
        if request.user.membership_tier:
            days_to_add = request.user.membership_tier.borrow_duration_days
            
        record.due_date += timedelta(days=days_to_add)
        record.renewal_count += 1
        record.save()
        
        messages.success(request, f"'{record.book.title}' renewed successfully. New due date: {record.due_date.strftime('%B %d, %Y')}")
        return redirect('my_books')

class ReserveBookView(LoginRequiredMixin, View):
    def post(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        
        # Only allow reservation if out of stock
        if book.available_copies > 0:
            messages.error(request, "This book is currently available. You can borrow it directly.")
            return redirect('book_detail', pk=pk)
            
        if Reservation.objects.filter(user=request.user, book=book, status='PENDING').exists():
            messages.warning(request, "You already have a pending reservation for this book.")
            return redirect('book_detail', pk=pk)

        Reservation.objects.create(user=request.user, book=book)
        messages.success(request, f"You have successfully reserved '{book.title}'. We will notify you when it returns.")
        return redirect('book_detail', pk=pk)

class ReturnBookView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    template_name = 'circulation/return_book.html'

    def get_context_data(self):
        today = timezone.now().date()
        context = {
            'returned_today_count': BorrowRecord.objects.filter(return_date__date=today).count(),
            'recent_returns': BorrowRecord.objects.filter(status='RETURNED').select_related('user', 'book').order_by('-return_date')[:5],
            'members': User.objects.filter(role='MEMBER').values('username')
        }
        return context

    def get(self, request):
        search_query = request.GET.get('username', '')
        records = []
        if search_query:
            records = BorrowRecord.objects.filter(user__username__icontains=search_query, status='ISSUED')
        
        context = self.get_context_data()
        context.update({
            'records': records,
            'search_query': search_query,
        })
        return render(request, self.template_name, context)

    def post(self, request):
        record_id = request.POST.get('record_id')
        action = request.POST.get('action', 'return')
        
        if not record_id:
            messages.error(request, "Invalid Request")
            return redirect('return_book')

        record = get_object_or_404(BorrowRecord, id=record_id, status='ISSUED')
        
        if action == 'mark_lost':
            record.status = 'LOST'
            record.fine_amount = record.book.price + Decimal('5.00')
            record.save()
            messages.error(request, f"'{record.book.title}' marked as LOST.")
            return redirect(f"{reverse('return_book')}?username={record.user.username}")

        # Check for Fine logic
        now = timezone.now()
        fine_amount = Decimal('0.00')
        overdue_days = 0
        
        if now > record.due_date:
            overdue_days = (now - record.due_date).days
            if overdue_days > 0:
                config = LibraryConfiguration.load()
                fine_amount = overdue_days * config.fine_per_day

        # 1. Initial Click (Action is 'return') -> Show Confirmation if fine exists
        if action == 'return':
            if fine_amount > 0:
                return render(request, 'circulation/fine_confirmation.html', {
                    'record': record,
                    'fine_amount': fine_amount,
                    'overdue_days': overdue_days
                })
            else:
                # No fine, proceed with standard return
                final_fine = Decimal('0.00')

        # 2. Pay Now Clicked
        elif action == 'return_pay_now':
            final_fine = Decimal('0.00') # Cleared immediately
            messages.success(request, f"Returned '{record.book.title}'. Fine of ₹{fine_amount} PAID.")

        # 3. Pay Later Clicked
        elif action == 'return_pay_later':
            final_fine = fine_amount # Added to account
            messages.warning(request, f"Returned '{record.book.title}'. Fine of ₹{final_fine} added to account.")
        
        else:
            return redirect('return_book')

        # Process Return (Common Logic)
        record.return_date = now
        record.status = 'RETURNED'
        record.fine_amount = final_fine
        record.save()
        
        # Reservation Check
        res = Reservation.objects.filter(book=record.book, status='PENDING').order_by('reserved_date').first()
        if res:
            messages.info(request, f"HOLD ALERT: This copy of '{record.book.title}' is reserved for {res.user.username}. Please set it aside.")
            record.book.status = 'RESERVED'
            record.book.save()
            
            # Notify Reserver
            Notification.objects.create(
                user=res.user,
                message=f"Good news! '{record.book.title}' is now available for you to pick up."
            )
        else:
            # Increment Stock
            record.book.available_copies += 1
            record.book.save()

        # Notify Borrower
        Notification.objects.create(
            user=record.user,
            message=f"You have returned '{record.book.title}'. Thank you!"
        )

        # Standard success message if no fine was involved (to avoid double messaging)
        if fine_amount == 0:
            messages.success(request, f"Returned '{record.book.title}' from {record.user.username}.")
        
        return redirect(f"{reverse('return_book')}?username={record.user.username}")

class ReservationListView(LoginRequiredMixin, LibrarianRequiredMixin, ListView):
    model = Reservation
    template_name = 'circulation/reservation_list.html'
    context_object_name = 'reservations'
    queryset = Reservation.objects.filter(status='PENDING').order_by('reserved_date')

class MemberBorrowListView(LoginRequiredMixin, ListView):
    model = BorrowRecord
    template_name = 'circulation/my_books.html'
    context_object_name = 'borrow_records'

    def get_queryset(self):
        return BorrowRecord.objects.filter(user=self.request.user).order_by('-issued_date')