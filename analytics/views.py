from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, FormView
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import timedelta
from circulation.models import BorrowRecord
from books.models import Book
from .forms import ReportFilterForm

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['LIBRARIAN', 'ADMIN']

class ReportBuilderView(LoginRequiredMixin, LibrarianRequiredMixin, FormView):
    template_name = 'analytics/report_builder.html'
    form_class = ReportFilterForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Default empty results
        context['report_data'] = None
        
        if self.request.GET:
            form = self.form_class(self.request.GET)
            if form.is_valid():
                start_date = form.cleaned_data['start_date']
                end_date = form.cleaned_data['end_date']
                report_type = form.cleaned_data['report_type']
                
                context['start_date'] = start_date
                context['end_date'] = end_date
                context['report_type_label'] = dict(form.fields['report_type'].choices)[report_type]

                if report_type == 'borrow_history':
                    context['report_data'] = BorrowRecord.objects.filter(
                        issued_date__date__range=[start_date, end_date]
                    ).select_related('user', 'book').order_by('-issued_date')
                    context['headers'] = ['Date', 'Member', 'Book', 'Status']
                    
                elif report_type == 'overdue_report':
                    context['report_data'] = BorrowRecord.objects.filter(
                        status='ISSUED',
                        due_date__date__lte=end_date
                    ).select_related('user', 'book').order_by('due_date')
                    context['headers'] = ['Due Date', 'Member', 'Book', 'Days Overdue']
                    
                elif report_type == 'fines_report':
                    context['report_data'] = BorrowRecord.objects.filter(
                        return_date__date__range=[start_date, end_date],
                        fine_amount__gt=0
                    ).select_related('user', 'book').order_by('-return_date')
                    context['headers'] = ['Return Date', 'Member', 'Book', 'Fine Amount']
                    context['total_amount'] = context['report_data'].aggregate(Sum('fine_amount'))['fine_amount__sum']

        return context

    def get_initial(self):
        # Pre-fill form with GET params if they exist, else defaults
        initial = super().get_initial()
        if 'start_date' in self.request.GET:
            initial['start_date'] = self.request.GET.get('start_date')
        if 'end_date' in self.request.GET:
            initial['end_date'] = self.request.GET.get('end_date')
        if 'report_type' in self.request.GET:
            initial['report_type'] = self.request.GET.get('report_type')
        return initial

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
        context['borrowed_books_list'] = BorrowRecord.objects.filter(
            issued_date__gte=start_of_month
        ).select_related('user', 'book').order_by('-issued_date')[:5]

        # 2. Total Fines Collected (Sum of fine_amount for RETURNED books)
        context['total_fines'] = BorrowRecord.objects.filter(
            status='RETURNED'
        ).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0.00
        context['fine_payment_list'] = BorrowRecord.objects.filter(
            status='RETURNED',
            fine_amount__gt=0
        ).select_related('user', 'book').order_by('-return_date')[:5]

        # 3. Most Popular Books
        context['popular_books'] = Book.objects.annotate(
            borrow_count=Count('borrow_records')
        ).order_by('-borrow_count')[:5]

        # 4. Overdue Books Count
        context['overdue_count'] = BorrowRecord.objects.filter(
            status='ISSUED',
            due_date__lt=now
        ).count()
        context['overdue_books_list'] = BorrowRecord.objects.filter(
            status='ISSUED',
            due_date__lt=now
        ).select_related('user', 'book').order_by('due_date')[:5]

        # 5. Lost Books Count
        context['lost_count'] = BorrowRecord.objects.filter(status='LOST').count()
        context['lost_books_list'] = BorrowRecord.objects.filter(status='LOST').select_related('user', 'book').order_by('-issued_date')[:5]

        return context