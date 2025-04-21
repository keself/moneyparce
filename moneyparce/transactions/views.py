from django.shortcuts import render, redirect

# Create your views here.
from .forms import TransactionForm
from .models import Transaction
from django.contrib.auth.decorators import login_required

#can only see transactions when youre logged in
@login_required
def transactions(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid(): #cecks if all fields were filled out
            amount = form.cleaned_data['amount']
            timestamp = form.cleaned_data['date']
            action = form.cleaned_data['action']

            transaction = Transaction(user=request.user, amount=amount, action=action, timestamp=timestamp)
            transaction.save()

            return redirect('transactions')

    else:
        form = TransactionForm()

    user_transactions = Transaction.objects.filter(user=request.user)
    total_balance = 0
    for transaction in user_transactions:
        if transaction.action == 'add':
            total_balance += transaction.amount
        elif transaction.action == 'remove':
            total_balance -= transaction.amount

    return render(request, 'transactions/transactions.html', {
        'form': form,
        'user_transactions': user_transactions,
        'total_balance': total_balance
    })