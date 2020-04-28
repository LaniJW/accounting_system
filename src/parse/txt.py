import logging

import parse.util


def txtify_bill(json_bill):
    contractor_name_address = '{}\n{}\n{} {}\n{} {}\n{}'.format(
        json_bill['commission']['contractor']['company_name'],
        json_bill['commission']['contractor']['contact_name'],
        json_bill['commission']['contractor']['address']['street']['street'],
        json_bill['commission']['contractor']['address']['street']['number'],
        json_bill['commission']['contractor']['address']['city']['plz'],
        json_bill['commission']['contractor']['address']['city']['city'],
        json_bill['commission']['contractor']['company_id'])
    logging.info('Added contractor name and address to TXT.')

    contractor_name_date = '{}, den {}.{}.{}'.format(
        json_bill['commission']['contractor']['address']['city']['city'],
        json_bill['commission']['date']['day'],
        json_bill['commission']['date']['month'],
        json_bill['commission']['date']['year'])
    logging.info('Added contractor name and date to TXT.')

    client_address = '{}{}\n{}{} {}\n{}{} {}'.format(
        get_multiple_chars('\t', 12),
        json_bill['commission']['client']['company_name'],
        get_multiple_chars('\t', 12),
        json_bill['commission']['client']['address']['street']['street'],
        json_bill['commission']['client']['address']['street']['number'],
        get_multiple_chars('\t', 12),
        json_bill['commission']['client']['address']['city']['plz'],
        json_bill['commission']['client']['address']['city']['city'])
    logging.info('Added client address to TXT.')

    pre_item_details = 'Kundennummer:\t{}\nAuftragsnummer:\t{}'.format(
        json_bill['commission']['contractor']['client_id'],
        json_bill['commission']['number'])
    logging.info('Added pre-item details to TXT.')

    bill_detail_header = 'Rechnung Nr{}{}'.format(get_multiple_chars('\t', 3),
                                                  json_bill['bill_nr'])
    bill_detail_separator = get_multiple_chars('-', len(bill_detail_header))
    bill_item_template = '\t{}\t{}\t\t{}\t{}\t{}\t{}\t{}'
    bill_items = ''
    for i, item in enumerate(json_bill['items']):
        bill_items += bill_item_template.format(item['id'], item['description'],
                                                item['amount'],
                                                item['price_per_item'], 'CHF',
                                                item['price_total'],
                                                item['tax'])
        if not i >= len(json_bill['items']) - 1:
            bill_items += '\n'
    bill_total_separator = get_multiple_chars('-', 50)
    bill_total = '{}Total CHF{}{}'.format(get_multiple_chars('\t', 11),
                                          get_multiple_chars('\t', 2),
                                          parse.util.get_total_price(
                                              json_bill['items']))
    bill_vat = '{}MWST CHF{}{}'.format(get_multiple_chars('\t', 11),
                                       get_multiple_chars('\t', 2),
                                       '0.00')
    logging.info('Added bill items to TXT.')

    due_date = 'Zahlungsziel ohne Abzug {} Tage ({})'.format(
        json_bill['commission']['deadline_days'], str(
            parse.util.get_due_date(
                parse.util.get_date_time_from_json(
                    json_bill['commission']['date'],
                    json_bill['commission']['time']),
                json_bill['commission']['deadline_days'])))
    payment_slip = 'Einzahlungsschein'
    logging.info('Added due date to TXT.')

    pre_second_client_addr_total = '\t{}{}{}'.format(parse.util.get_total_price(
        json_bill['items']), get_multiple_chars('\t', 5),
        parse.util.get_total_price(
            json_bill['items']))
    some_digits = '0 00000 00000 00000'
    third_address = client_address.replace('\t', '')
    logging.info('Added addresses to TXT.')

    return '{}\n\n\n\n\n{}\n{}\n{}\n\n{}\n{}\n{}\n{}\n{}\n\n{}\n\n\n\n\n\n\n\n\n\n{}\n\n{}\n\n\n\n\n\n\n\n\n\n{}\n{}\n{}\n\n{}'.format(
        contractor_name_address, contractor_name_date, client_address,
        pre_item_details, bill_detail_header, bill_detail_separator, bill_items,
        bill_total_separator, bill_total, bill_vat, due_date, payment_slip,
        pre_second_client_addr_total, client_address, some_digits,
        third_address)


def get_multiple_chars(c, n):
    chars = ''
    for i in range(n):
        chars += c
    return chars
