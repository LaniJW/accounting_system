def get_total_price(items):
    amount = 0
    for item in items:
        amount += float(item['price_total'])
    return amount