from django import forms
from .models import LibraryConfiguration
from accounts.models import MembershipTier

class LibraryConfigurationForm(forms.ModelForm):
    class Meta:
        model = LibraryConfiguration
        fields = ['fine_per_day', 'hold_expiry_days']
        widgets = {
            'fine_per_day': forms.NumberInput(attrs={'step': '0.01'}),
        }

class MembershipTierForm(forms.ModelForm):
    class Meta:
        model = MembershipTier
        fields = ['name', 'max_books', 'borrow_duration_days', 'max_renewals', 'subscription_fee', 'is_active']
