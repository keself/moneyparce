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
        if form.is_valid():  # checks if all fields were filled out
            amount = form.cleaned_data['amount']
            timestamp = form.cleaned_data['date']
            action = form.cleaned_data['action']
            category = form.cleaned_data['category']

            transaction = Transaction(user=request.user, amount=amount, action=action, timestamp=timestamp)
            transaction.save()

            if action == 'remove' or action == 'add':
                today = timezone.now().date()

                 # Sum up all budgets for this category within the active date range
                total_budget = Budget.objects.filter(
                    category=category,
                    start_date__lte=today,
                    end_date__gte=today
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Sum up all 'remove' transactions for this category by the user
                total_spent = Transaction.objects.filter(
                    user=request.user,
                    category=category,
                    action='remove'
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Sum up all 'add' transactions for this category by the user
                total_added = Transaction.objects.filter(
                    user=request.user,
                    category=category,
                    action='add'
                ).aggregate(total=Sum('amount'))['total'] or 0

                # Calculate the net spent (removes - adds)
                net_spent = total_spent - total_added

                # Calculate the percent of budget used
                percent_used = (net_spent / total_budget) * 100 if total_budget > 0 else 0

                if total_budget > 0:
                    if net_spent > total_budget:
                        messages.error(request, f"You've exceeded your budget for {category}! (Limit: ${total_budget}, Net Spent: ${net_spent})")
                    elif net_spent == total_budget:
                        messages.info(request, f"You've met your budget limit for {category}. (Limit: ${total_budget}, Net Spent: ${net_spent})")
                    elif percent_used >= 90:
                        messages.warning(request, f"You're approaching your budget limit for {category}. (Limit: ${total_budget}, Net Spent: ${net_spent})")

            messages.success(request, f"Transaction successful for {category}.")
            return redirect('transactions')

    else:
        form = TransactionForm()

    # Calculate total balance for the user
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
