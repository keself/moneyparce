from django import forms

class TransactionForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2, min_value=0)
    action = forms.ChoiceField(choices=[('add', 'Add'), ('remove', 'Remove')])
    timestamp = forms.DateInput(attrs={'type': 'date'})