import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from budgets.models import Budget
from transactions.models import Transaction

@login_required
def download_data(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="moneyparce_data.csv"'

    info_displayed = csv.writer(response)
    
    info_displayed.writerow(['Budgets'])
    info_displayed.writerow(['Name', 'Amount', 'Category']) 

    budgets = Budget.objects.all()
    for b in budgets:
        info_displayed.writerow([b.name, b.amount, b.category])

    info_displayed.writerow([])  

    info_displayed.writerow(['Transactions'])
    info_displayed.writerow(['Amount', 'Action', 'Category'])  

    transactions = Transaction.objects.filter(user=request.user)
    for i in transactions:
        info_displayed.writerow([i.amount, i.action, i.category])  
    
    total_balance = 0
    for j in transactions:
        if j.action == 'add':
            total_balance += j.amount
        elif j.action == 'remove':
            total_balance -= j.amount

    info_displayed.writerow([]) 
    info_displayed.writerow(['Total Balance'])
    info_displayed.writerow([f"${total_balance:.2f}"])

    return response
