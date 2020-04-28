import logging
import re

MIN_LINES = 4

BILLING_LINE_INDEX = 0
CONTRACTOR_LINE_INDEX = 1
CLIENT_LINE_INDEX = 2
INVOICE_ITEMS_STARTING_INDEX = 3

BILLING_COLUMN_COUNT = 6
CONTRACTOR_COLUMN_COUNT = 8
CLIENT_COLUMN_COUNT = 5
INVOICE_ITEMS_COLUMN_COUNT = 7

NAME_PATTERN = r'(?:\w+ )+(?:\w+)'
STREET_NUMBER_PATTERN = r'(?:\w+ )+\w+'
ZIP_CITY_PATTERN = r'\w+ (?:\w+ )*\w+'


def check_bill_format(bill):
    lines = bill.split('\n')
    lines.remove('')
    check_passed = True

    check_passed = check_passed if check_line_count(lines,
                                                    check_passed) else False
    check_passed = check_passed if check_item_in_lines_count(lines,
                                                             check_passed) else False
    check_passed = check_passed if check_billing_line_format(
        lines[BILLING_LINE_INDEX], check_passed) else False
    check_passed = check_passed if check_contractor_line_format(
        lines[CONTRACTOR_LINE_INDEX], check_passed) else False
    check_passed = check_passed if check_client_line_format(
        lines[CLIENT_LINE_INDEX], check_passed) else False
    check_passed = check_passed if check_invoice_item_lines_format(
        lines[INVOICE_ITEMS_STARTING_INDEX:], check_passed) else False

    logging.info(f'Invoice format check passed: {check_passed}')
    return check_passed


def check_line_count(lines, check_passed):
    if not check_passed:
        return check_passed

    if not len(lines) >= MIN_LINES:
        logging.warning(
            f'Not enough lines. Minimum has to be {MIN_LINES}, otherwise there\'s not enough space for invoice items.')
        return False

    logging.info(f'Line count check passed: {True}')

    return True


def check_item_in_lines_count(lines, check_passed):
    if not check_passed:
        return check_passed

    billing_column_count = len(lines[BILLING_LINE_INDEX].split(';'))
    contractor_column_count = len(lines[CONTRACTOR_LINE_INDEX].split(';'))
    client_column_count = len(lines[CLIENT_LINE_INDEX].split(';'))
    invoice_item_lines = lines[INVOICE_ITEMS_STARTING_INDEX:]

    if billing_column_count != BILLING_COLUMN_COUNT:
        logging.warning(
            f'Not enough columns ({billing_column_count}) in billing line (i = {BILLING_LINE_INDEX}). Billing line: "{billing_column_count}"')
        return False
    if contractor_column_count != CONTRACTOR_COLUMN_COUNT:
        logging.warning(
            f'Not enough columns ({contractor_column_count}) in contractor line (i = {CONTRACTOR_LINE_INDEX}). Contractor line: "{contractor_column_count}"')
        return False
    if client_column_count != CLIENT_COLUMN_COUNT:
        logging.warning(
            f'Not enough columns ({client_column_count}) in client line (i = {CLIENT_LINE_INDEX}). Client line: "{client_column_count}"')
        return False
    for i, invoice_item_line in enumerate(invoice_item_lines):
        invoice_item_column_count = len(invoice_item_line.split(';'))
        if invoice_item_column_count != INVOICE_ITEMS_COLUMN_COUNT:
            logging.warning(
                f'Not enough columns ({invoice_item_column_count}) in invoice item line (i = {i}). Client line: "{invoice_item_line}"')
            return False

    logging.info(f'Column count check passed: {True}')

    return True


def check_billing_line_format(line, check_passed):
    if not check_passed:
        return check_passed

    check_failed = False

    columns = line.split(';')
    row_id = columns[0]
    commission_number = columns[1]
    billing_location = columns[2]
    billing_date = columns[3]
    billing_timestamp = columns[4]
    deadline = columns[5]

    row_id_p = r'Rechnung_\d+'
    if not re.match(row_id_p, row_id):
        logging.warning(
            f'Billing row id ({row_id}) didn\'t match pattern "{row_id_p}".')
        check_failed = True

    commission_number_p = r'Auftrag_\w+'
    if not re.match(commission_number_p, commission_number):
        logging.warning(
            f'Billing commission number ({commission_number}) didn\'t match pattern "{commission_number_p}".')
        check_failed = True

    billing_location_p = r'.+'
    if not re.match(billing_location_p, billing_location):
        logging.warning(
            f'Billing location ({billing_location}) didn\'t match pattern "{billing_location_p}".')
        check_failed = True

    billing_date_p = r'\d{2}\.\d{2}\.\d{4}'
    if not re.match(billing_date_p, billing_date):
        logging.warning(
            f'Billing date ({billing_date}) didn\'t match pattern "{billing_date_p}".')
        check_failed = True

    billing_timestamp_p = r'\d{1,2}:\d{1,2}:\d{1,2}'
    if not re.match(billing_timestamp_p, billing_timestamp):
        logging.warning(
            f'Billing timestamp ({billing_timestamp}) didn\'t match pattern "{billing_timestamp_p}".')
        check_failed = True

    deadline_p = r'ZahlungszielInTagen_\d+'
    if not re.match(deadline_p, deadline):
        logging.warning(
            f'Deadline ({deadline}) didn\'t match pattern "{deadline_p}".')
        check_failed = True

    logging.info(f'Billing line check passed: {not check_failed}')

    return not check_failed


def check_contractor_line_format(line, check_passed):
    if not check_passed:
        return check_passed

    check_failed = False

    columns = line.split(';')
    row_id = columns[0]
    contractor_id = columns[1]
    salutation = columns[2]
    name = columns[3]
    street_and_number = columns[4]
    zip_and_city = columns[5]
    company_id = columns[6]
    email_address = columns[7]

    row_id_m = 'Herkunft'
    if row_id != row_id_m:
        logging.info(
            f'Contractor row id ({row_id}) didn\'t match "{row_id_m}".')
        check_failed = True

    contractor_id_p = r'.+'
    if not re.match(contractor_id_p, contractor_id):
        logging.warning(
            f'Contractor customer id ({contractor_id}) didn\'t match "{contractor_id_p}".')
        check_failed = True

    salutation_p = r'.+'
    if not re.match(salutation_p, salutation):
        logging.warning(
            f'Contractor salutation ({salutation}) didn\'t match "{salutation_p}".')
        check_failed = True

    if not check_name_format(name):
        logging.warning(
            f'Contractor name ({name}) didn\'t match "{NAME_PATTERN}".')
        check_failed = True

    if not check_street_and_number_format(street_and_number):
        logging.warning(
            f'Contractor street and number ({street_and_number}) didn\'t match "{STREET_NUMBER_PATTERN}".')
        check_failed = True

    if not check_zip_and_city_format(zip_and_city):
        logging.warning(
            f'Contractor zip code and city ({zip_and_city}) didn\'t match "{ZIP_CITY_PATTERN}".')
        check_failed = True

    company_id_p = r'[A-Z]{3}-(?:\d{3}.){2}\d{3} MWST'
    if not re.match(company_id_p, company_id):
        logging.warning(
            f'Contractor company id ({company_id}) didn\'t match "{company_id_p}".')
        check_failed = True

    email_address_p = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    if not re.match(email_address_p, email_address):
        logging.warning(
            f'Contractor email address ({email_address}) didn\'t match "{email_address_p}".')
        check_failed = True

    logging.info(f'Contractor line check passed: {not check_failed}')

    return not check_failed


def check_client_line_format(line, check_passed):
    if not check_passed:
        return check_passed

    check_failed = False

    columns = line.split(';')
    row_id = columns[0]
    customer_id = columns[1]
    name = columns[2]
    street_and_number = columns[3]
    zip_and_city = columns[4]

    row_id_m = 'Endkunde'
    if row_id != row_id_m:
        logging.warning(f'Client row id ({row_id}) didn\'t match "{row_id_m}".')
        check_failed = True

    customer_id_p = '.+'
    if not re.match(customer_id_p, customer_id):
        logging.warning(
            f'Client customer id ({customer_id}) didn\'t match "{customer_id_p}".')
        check_failed = True

    if not check_name_format(name):
        logging.warning(f'Client name ({name}) didn\'t match "{NAME_PATTERN}".')
        check_failed = True

    if not check_street_and_number_format(street_and_number):
        logging.warning(
            f'Client street number ({street_and_number}) didn\'t match "{STREET_NUMBER_PATTERN}".')
        check_failed = True

    if not check_zip_and_city_format(zip_and_city):
        logging.warning(
            f'Client zip city ({street_and_number}) didn\'t match "{STREET_NUMBER_PATTERN}".')
        check_failed = True

    logging.info(f'Client line check passed: {not check_failed}')

    return not check_failed


def check_invoice_item_lines_format(lines, check_passed):
    if not check_passed:
        return check_passed

    check_failed = False

    for i, line in enumerate(lines):
        columns = line.split(';')
        row_id = columns[0]
        invoice_id = columns[1]
        invoice_desc = columns[2]
        count = columns[3]
        unit_price = columns[4]
        invoice_item_price = columns[5]
        vat = columns[6]

        row_id_m = 'RechnPos'
        if row_id != row_id_m:
            logging.warning(
                f'The row id ({row_id}) of the invoice item with the index {i} didn\'t match "{row_id_m}".')
            check_failed = True

        invoice_id_p = r'\d+'
        if not re.match(invoice_id_p, invoice_id):
            logging.warning(
                f'The invoice id ({invoice_id}) of the invoice item with the index {i} didn\'t match "{invoice_id_p}".')
            check_failed = True

        invoice_desc_p = r'.+'
        if not re.match(invoice_desc_p, invoice_desc):
            logging.warning(
                f'The invoice description ({invoice_desc}) of the invoice item with the index {i} didn\'t match "{invoice_desc_p}".')
            check_failed = True

        count_p = r'\d+'
        if not re.match(count_p, count):
            logging.warning(
                f'The item count ({count}) of the invoice item with the index {i} didn\'t match "{invoice_id_p}".')
            check_failed = True

        unit_price_p = r'\d+\.\d'
        if not re.match(unit_price_p, unit_price):
            logging.warning(
                f'The unit price ({unit_price}) of the invoice item with the index {i} didn\'t match "{unit_price_p}".')
            check_failed = True

        invoice_item_price_p = r'\d+\.\d'
        if not re.match(invoice_item_price_p, invoice_item_price):
            logging.warning(
                f'The total invoice item price ({invoice_item_price}) of the invoice item with the index {i} didn\'t match "{invoice_item_price_p}".')
            check_failed = True

        vat_m = 'MWST_0.00%'
        if vat != vat_m:
            logging.warning(
                f'The VAT ({vat}) of the invoice item with the index {i} didn\'t match "{vat_m}".')
            check_failed = True

        logging.info(f'Invoice items check passed: {not check_failed}')

        return not check_failed


def check_name_format(name):
    return re.match(NAME_PATTERN, name)


def check_street_and_number_format(san):
    return re.match(STREET_NUMBER_PATTERN, san)


def check_zip_and_city_format(zac):
    return re.match(ZIP_CITY_PATTERN, zac)
