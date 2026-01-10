from django.contrib import admin
from .models import BorrowRecord, Reservation

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'issued_date', 'due_date', 'status', 'fine_amount')
    list_filter = ('status', 'issued_date')
    search_fields = ('user__username', 'book__title', 'book__isbn')

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'reserved_date', 'status')
    list_filter = ('status',)