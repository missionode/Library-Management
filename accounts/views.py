from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, View, UpdateView, CreateView
from django.db.models import Sum, Q, Value, DecimalField
from django.db.models.functions import Coalesce
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from decimal import Decimal
from .forms import MemberRegistrationForm, UserProfileForm, LibrarianCreationForm
from .models import User, MembershipTier
from circulation.models import BorrowRecord

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['LIBRARIAN', 'ADMIN']

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role == 'ADMIN'

class CustomLoginView(LoginView):
    def get_success_url(self):
        user = self.request.user
        if user.role in ['LIBRARIAN', 'ADMIN']:
            return reverse('analytics_dashboard')
        return reverse('home')

class CreateLibrarianView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = LibrarianCreationForm
    template_name = 'accounts/create_librarian.html'
    success_url = reverse_lazy('member_list')

    def form_valid(self, form):
        messages.success(self.request, f"Librarian {form.instance.username} created successfully.")
        return super().form_valid(form)

class MemberManagementView(LoginRequiredMixin, LibrarianRequiredMixin, ListView):
    model = User
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    paginate_by = 10

    def get_queryset(self):
        # Base queryset: exclude Admins, annotate with total fines
        queryset = User.objects.exclude(role='ADMIN').annotate(
            total_fines=Coalesce(Sum('borrowed_books__fine_amount'), Value(Decimal('0.00'), output_field=DecimalField()))
        ).order_by('username')
        
        # Restriction: Librarians can ONLY see Members
        if self.request.user.role == 'LIBRARIAN':
            queryset = queryset.filter(role='MEMBER')
        
        # Search Filter
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
            
        # Role Filter
        role_filter = self.request.GET.get('role')
        if role_filter in ['MEMBER', 'LIBRARIAN']:
            queryset = queryset.filter(role=role_filter)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tiers'] = MembershipTier.objects.filter(is_active=True)
        return context

class ToggleMemberStatusView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        if member.role == 'ADMIN':
            messages.error(request, "Cannot modify Admin users.")
            return redirect('member_list')
            
        member.is_active_member = not member.is_active_member
        member.save()
        status = "Active" if member.is_active_member else "Blocked"
        messages.success(request, f"User {member.username} is now {status}.")
        return redirect('member_list')

class ChangeMembershipView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        if member.role == 'ADMIN':
             messages.error(request, "Cannot modify Admin users.")
             return redirect('member_list')

        tier_id = request.POST.get('tier_id')
        if tier_id:
            tier = get_object_or_404(MembershipTier, id=tier_id)
            member.membership_tier = tier
            member.save()
            messages.success(request, f"Updated {member.username} to {tier.name} tier.")
        return redirect('member_list')

class ClearFinesView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk)
        
        # Calculate amount to be cleared for logging (optional, could add Transaction model later)
        total_fines = BorrowRecord.objects.filter(user=member).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0.00
        
        if total_fines > 0:
            # Clear fines
            BorrowRecord.objects.filter(user=member).update(fine_amount=0.00)
            messages.success(request, f"Cleared ${total_fines} in fines for {member.username}.")
        else:
            messages.info(request, f"{member.username} has no outstanding fines.")
            
        return redirect('member_list')

class UserProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if user.is_authenticated:
            if user.role == 'MEMBER':
                # Stats for Member
                active_borrows = BorrowRecord.objects.filter(user=user, status='ISSUED')
                context['active_loans_count'] = active_borrows.count()
                context['total_fines'] = BorrowRecord.objects.filter(user=user).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0.00
                context['overdue_loans_count'] = 0
                for record in active_borrows:
                    if record.is_overdue:
                        context['overdue_loans_count'] += 1

            elif user.role in ['LIBRARIAN', 'ADMIN']:
                # Stats for Librarian/Admin
                context['total_active_loans'] = BorrowRecord.objects.filter(status='ISSUED').count()
                all_issued = BorrowRecord.objects.filter(status='ISSUED')
                context['total_overdue'] = sum(1 for r in all_issued if r.is_overdue)

        return context

def register(request):
    if request.method == 'POST':
        form = MemberRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = MemberRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})
