from django import forms
from .models import Transaction
from django.utils import timezone

class TransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')])

class TransactionForm(forms.ModelForm):
    timestamp = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M:%S'],
        initial=timezone.now,  # Pre-populate with current time; can be changed by the user
        required=False  # Allows the field to be optional. You can set this to True if desired.
    )
    class Meta:
        model = Transaction
        fields = ['amount', 'action', 'category']
