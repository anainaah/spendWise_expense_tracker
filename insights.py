from collections import defaultdict
from datetime import datetime

def generate_insight(expenses):
    # If the database has no expenses at all
    if not expenses:
        return "Add some expenses to see insights!"

    # Get the current month and last month in YYYY-MM format
    now = datetime.now()
    this_month = now.strftime("%Y-%m")
    
    # Calculate previous month (handling January wrap-around to December)
    last_month_num = now.month - 1 or 12
    last_month_year = now.year if now.month - 1 != 0 else now.year - 1
    last_month = f"{last_month_year}-{last_month_num:02d}"

    # Group totals by category for this month and last month
    this_month_by_cat = defaultdict(float)
    last_month_by_cat = defaultdict(float)

    for e in expenses:
        # Extract YYYY-MM from the date string 'YYYY-MM-DD'
        expense_month = e.date[:7]
        if expense_month == this_month:
            this_month_by_cat[e.category] += e.amount
        elif expense_month == last_month:
            last_month_by_cat[e.category] += e.amount

    # If there is no spending recorded for this month yet
    if not this_month_by_cat:
        return "No expenses logged this month yet. Start logging to get insights!"

    # Find the category with the highest spend this month
    top_category = max(this_month_by_cat, key=this_month_by_cat.get)
    this_val = this_month_by_cat[top_category]
    last_val = last_month_by_cat.get(top_category, 0)

    # If the user didn't spend anything on this category last month
    if last_val == 0:
        return f"Your top spending category this month is {top_category} (₹{this_val:.0f})."

    # Calculate percentage difference
    change = ((this_val - last_val) / last_val) * 100
    direction = "more" if change > 0 else "less"
    
    return f"You spent {abs(change):.0f}% {direction} on {top_category} this month than last month."