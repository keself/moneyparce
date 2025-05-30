from django import forms
from .models import Budget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'amount', 'category', 'start_date', 'end_date', 'notes']
        
        def __init__(self, *args, **kwargs):
            super(BudgetForm, self).__init__(*args, **kwargs)
            self.fields['category'].initial = 'Uncategorized'
            
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
