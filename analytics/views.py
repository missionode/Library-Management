from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from circulation.models import BorrowRecord
from books.models import Book

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['LIBRARIAN', 'ADMIN']

class AnalyticsDashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 1. Total Books Borrowed (This Month)
        context['borrowed_this_month'] = BorrowRecord.objects.filter(
            issued_date__gte=start_of_month
        ).count()

        # 2. Total Fines Collected (Sum of fine_amount for RETURNED books)
        context['total_fines'] = BorrowRecord.objects.filter(
            status='RETURNED'
        ).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0.00

        # 3. Most Popular Books
        context['popular_books'] = Book.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:5]

        # 4. Overdue Books Count
        context['overdue_count'] = BorrowRecord.objects.filter(
            status='ISSUED',
            due_date__lt=now
        ).count()

        # 5. Lost Books Count
        context['lost_count'] = BorrowRecord.objects.filter(status='LOST').count()

        return context