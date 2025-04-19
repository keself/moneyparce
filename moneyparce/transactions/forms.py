from django import forms
from .models import Transaction

class TransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')])

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'action', 'category']
