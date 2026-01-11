from django.contrib import admin
from .models import LibraryConfiguration

@admin.register(LibraryConfiguration)
class LibraryConfigurationAdmin(admin.ModelAdmin):
    list_display = ('fine_per_day', 'hold_expiry_days')
    
    def has_add_permission(self, request):
        # Only allow adding if no instance exists
        if LibraryConfiguration.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the singleton
        return False