from django import forms
from django.utils import timezone

class ReportFilterForm(forms.Form):
    REPORT_TYPES = [
        ('borrow_history', 'Borrowing History'),
        ('overdue_report', 'Overdue Books'),
        ('fines_report', 'Fines Collected'),
    ]
    
    start_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg'})
    )
    end_date = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border rounded-lg'})
    )
    report_type = forms.ChoiceField(
        choices=REPORT_TYPES,
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded-lg'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        
        if not start:
            cleaned_data['start_date'] = timezone.now().date() - timezone.timedelta(days=30)
        if not end:
            cleaned_data['end_date'] = timezone.now().date()
            
        return cleaned_data
