from django.shortcuts import render, redirect

# Create your views here.
from .forms import TransactionForm
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from budgets.models import Budget
from django.db.models import Sum
from django.utils import timezone

#can only see transactions when youre logged in
@login_required
def transactions(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid(): #cecks if all fields were filled out
            amount = form.cleaned_data['amount']
            action = form.cleaned_data['action']
            category = form.cleaned_data['category']

            transaction = Transaction(user=request.user, amount=amount, action=action)
            transaction.save()

            if action == 'remove':
                today = timezone.now().date()

                budget = Budget.objects.filter(
                    category=category,
                    start_date__lte=today,
                    end_date__gte=today
                ).first()

                if budget:
                    total_spent = Transaction.objects.filter(
                        user=request.user,
                        category=category,
                        action='remove'
                    ).aggregate(total=Sum('amount'))['total'] or 0

                    percent_used = (total_spent / budget.amount) * 100

                    if percent_used >= 100:
                        messages.error(request, f"You've exceeded your budget for {category}! (Limit: ${budget.amount}, Spent: ${total_spent})")
                    elif percent_used >= 90:
                        messages.warning(request, f"You're approaching your budget limit for {category}. (Limit: ${budget.amount}, Spent: ${total_spent})")

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
