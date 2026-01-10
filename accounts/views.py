from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView, ListView, View
from django.db.models import Sum, Q
from django.contrib import messages
from .forms import MemberRegistrationForm
from .models import User, MembershipTier
from circulation.models import BorrowRecord

class LibrarianRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               self.request.user.role in ['LIBRARIAN', 'ADMIN']

class MemberManagementView(LoginRequiredMixin, LibrarianRequiredMixin, ListView):
    model = User
    template_name = 'accounts/member_list.html'
    context_object_name = 'members'
    paginate_by = 10

    def get_queryset(self):
        queryset = User.objects.filter(role='MEMBER').order_by('username')
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(username__icontains=q) |
                Q(first_name__icontains=q) |
                Q(last_name__icontains=q) |
                Q(email__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tiers'] = MembershipTier.objects.filter(is_active=True)
        return context

class ToggleMemberStatusView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk, role='MEMBER')
        member.is_active_member = not member.is_active_member
        member.save()
        status = "Active" if member.is_active_member else "Blocked"
        messages.success(request, f"Member {member.username} is now {status}.")
        return redirect('member_list')

class ChangeMembershipView(LoginRequiredMixin, LibrarianRequiredMixin, View):
    def post(self, request, pk):
        member = get_object_or_404(User, pk=pk, role='MEMBER')
        tier_id = request.POST.get('tier_id')
        if tier_id:
            tier = get_object_or_404(MembershipTier, id=tier_id)
            member.membership_tier = tier
            member.save()
            messages.success(request, f"Updated {member.username} to {tier.name} tier.")
        return redirect('member_list')

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
