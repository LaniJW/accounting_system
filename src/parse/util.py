import datetime


def get_total_price(items):
    amount = 0
    for item in items:
        amount += float(item['price_total'])
    return amount


def get_due_date(date_of_issue, deadline_days):
    return date_of_issue + datetime.timedelta(days=int(deadline_days))


def get_date_time_from_json(date_json, time_json):
    return datetime.datetime(year=int(date_json['year']),
                             month=int(date_json['month']),
                             day=int(date_json['day']),
                             hour=int(time_json['hour']),
                             minute=int(time_json['minute']),
                             second=int(time_json['second']))
