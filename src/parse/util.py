import datetime


def get_total_price(items):
    amount = 0
    for item in items:
        amount += float(item['price_total'])
    return amount


def get_due_date(date_of_issue, deadline_days):
    return date_of_issue + datetime.timedelta(days=int(deadline_days))
