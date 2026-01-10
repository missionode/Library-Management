from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, MembershipTier

@admin.register(MembershipTier)
class MembershipTierAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_books', 'borrow_duration_days', 'subscription_fee', 'is_active')

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'membership_tier', 'is_active_member', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Library Profile', {'fields': ('role', 'membership_tier', 'is_active_member', 'phone_number', 'address', 'profile_image')}),
    )

admin.site.register(User, CustomUserAdmin)