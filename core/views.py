from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, View, TemplateView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Notification, LibraryConfiguration
from accounts.models import MembershipTier
from .forms import LibraryConfigurationForm, MembershipTierForm

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'ADMIN'

class PrivacyView(TemplateView):
    template_name = 'legal/privacy.html'

class TermsView(TemplateView):
    template_name = 'legal/terms.html'

# --- Settings Views ---

class SettingsDashboardView(LoginRequiredMixin, AdminRequiredMixin, TemplateView):
    template_name = 'core/settings_dashboard.html'

class LibraryConfigurationUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = LibraryConfiguration
    form_class = LibraryConfigurationForm
    template_name = 'core/settings_config_form.html'
    success_url = reverse_lazy('settings_dashboard')

    def get_object(self, queryset=None):
        return LibraryConfiguration.load()

class MembershipTierListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = MembershipTier
    template_name = 'core/settings_tier_list.html'
    context_object_name = 'tiers'

class MembershipTierCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = MembershipTier
    form_class = MembershipTierForm
    template_name = 'core/settings_tier_form.html'
    success_url = reverse_lazy('settings_tier_list')

class MembershipTierUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = MembershipTier
    form_class = MembershipTierForm
    template_name = 'core/settings_tier_form.html'
    success_url = reverse_lazy('settings_tier_list')

# --- Notification Views ---

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'core/notifications.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class MarkNotificationReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, user=request.user)
        notification.is_read = True
        notification.save()
        return JsonResponse({'status': 'success'})

class MarkAllNotificationsReadView(LoginRequiredMixin, View):
    def post(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return redirect('notifications')