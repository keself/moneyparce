from django.shortcuts import render
from datetime import date, timedelta
from transactions.models import Transaction
from budgets.models import Budget
import calendar

def index(request):
    curr_user = request.user
    today = date.today()
    start_date = today.replace(day=1)
    last_day = calendar.monthrange(today.year, today.month)[1]
    end_date = today.replace(day=last_day)
    past_transactions = Transaction.objects.filter(user=curr_user, timestamp__date__lte=today).order_by('timestamp')
    planned_transactions = Transaction.objects.filter(user=curr_user, timestamp__date__gt=today).order_by('timestamp')

    daily_data = {}
    cumulative_balance = 0
    num_days = (end_date - start_date).days + 1

    # Build daily data for every day of the month
    for i in range(num_days):
        day = start_date + timedelta(days=i)
        day_transactions = past_transactions.filter(timestamp__date=day)
        day_sum = sum(
            t.amount if t.action == 'add' else -t.amount 
            for t in day_transactions
        )
        cumulative_balance += day_sum
        # For days in the future, we'll initially set both values to today's cumulative_balance
        daily_data[day] = {
            'actual': cumulative_balance,
            'projected': cumulative_balance
        }

    # Then update projected balance for days after today based on planned transactions.
    projected_balance = daily_data[today]['actual'] if today in daily_data else 0
    for i in range(1, (end_date - today).days + 1):
        day = today + timedelta(days=i)
        day_planned = planned_transactions.filter(timestamp__date=day)
        planned_sum = sum(
            t.amount if t.action == 'add' else -t.amount 
            for t in day_planned
        )
        projected_balance += planned_sum
        if day in daily_data:
            daily_data[day]['projected'] = projected_balance

    budget_qs = Budget.objects.filter(user=curr_user)
    if budget_qs.exists():
        budget_value = float(budget_qs.order_by("-id").first().amount)
    else:
        budget_value = 0

    graph_rows = []
    graph_rows.append(['Date', 'Actual Balance', 'Projected Balance', 'Total Budget'])
    
    # For each day, only include the actual balance until today.
    for day in sorted(daily_data.keys()):
        # Only show actual balance up to and including today
        actual = daily_data[day]['actual'] if day <= today else None
        projected = daily_data[day]['projected']
        graph_rows.append([
            day.strftime("%Y-%m-%d"),
            actual,  # Python None becomes null in JSON
            float(projected),
            budget_value
        ])

    context = {
        'graph_data': graph_rows
    }
    
    return render(request, 'data/month_graph.html', context)
