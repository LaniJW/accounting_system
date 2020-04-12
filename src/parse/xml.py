import datetime
import xml.etree.cElementTree as et

CONFIG = None

def xmlify_bill(json_bill, config):
    global CONFIG

    root = et.Element('Invoice', version='3.1', doctype='ETS Invoice')
    CONFIG = config

    add_invoice_header(root, json_bill)

    # TODO(laniw): Add converters for invoice details and invoice summary.

    tree = et.ElementTree(root)
    tree.write('bill.xml')
    return et.tostring(root, 'utf8')


def add_invoice_header(root, json_bill):
    invoice_header = et.SubElement(root, 'Invoice_Header')

    basedata = et.SubElement(invoice_header, 'I.H.010_Basisdaten')
    et.SubElement(basedata, 'BV.010_Rechnungsnummer').text = json_bill['commission']['name']
    et.SubElement(basedata, 'BV.020_Rechnungsdatum').text = str(
        get_date_time_from_json(json_bill['commission']['date'], json_bill['commission']['time']))
    et.SubElement(basedata, 'BV.030_Funktion_des_Dokuments').text = 'Original'
    et.SubElement(basedata, 'BV.040_Typ_des_Dokuments').text = 'Rechnung'
    et.SubElement(basedata, 'BV.050_Rechnungs_Endkennzeichen').text = 'vollstaendige Rechnung'
    et.SubElement(basedata, 'BV.060_Bestellnummer_des_Kaeufers')
    et.SubElement(basedata, 'BV.080_Waehrung').text = 'CHF'
    et.SubElement(basedata, 'BV.090_Sprache').text = 'de'

    client_identification = et.SubElement(invoice_header, 'I.H.020_Einkaeufer_Identifikation')
    et.SubElement(client_identification, 'BV.010_Nr_Kaeufer_beim_Lieferanten').text = 'undef'
    et.SubElement(client_identification, 'BV.020_Nr_Kaeufer_beim_Kaeufer').text = json_bill['commission']['contractor'][
        'client_id']
    et.SubElement(client_identification, 'BV.030_Nr_Kaeufer_bei_ETS').text = json_bill['commission']['client'][
        'client_id']
    et.SubElement(client_identification, 'BV.035_Typ_der_Handelsplatz_ID').text = 'TPID'
    et.SubElement(client_identification, 'BV.040_Name1').text = json_bill['commission']['client']['company_name']
    et.SubElement(client_identification, 'BV.100_PLZ').text = json_bill['commission']['client']['address']['city'][
        'plz']
    et.SubElement(client_identification, 'BV.110_Stadt').text = json_bill['commission']['client']['address']['city'][
        'city']
    et.SubElement(client_identification, 'BV.120_Land').text = 'CH'

    contractor_identification = et.SubElement(invoice_header, 'I.H.030_Lieferanten_Identifikation')
    et.SubElement(contractor_identification, 'BV.010_Nr_Lieferant_beim_Kaeufer').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(contractor_identification, 'BV.030_Nr_Lieferant_bei_ETS').text = CONFIG['data']['email_address']
    et.SubElement(contractor_identification, 'BV.040_Name1').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(contractor_identification, 'BV.070_Strasse').text = \
        json_bill['commission']['contractor']['address']['street']['street']
    et.SubElement(contractor_identification, 'BV.100_PLZ').text = \
        json_bill['commission']['contractor']['address']['city']['plz']
    et.SubElement(contractor_identification, 'BV.110_Stadt').text = \
        json_bill['commission']['contractor']['address']['city']['city']
    et.SubElement(contractor_identification, 'BV.120_Land').text = 'CH'

    billing_address = et.SubElement(invoice_header, 'I.H.040_Rechnungsadresse')
    et.SubElement(billing_address, 'BV.040_Name1').text = json_bill['commission']['client']['company_name']
    et.SubElement(billing_address, 'BV.100_PLZ').text = json_bill['commission']['client']['address']['city']['plz']
    et.SubElement(billing_address, 'BV.110_Stadt').text = json_bill['commission']['client']['address']['city']['city']
    et.SubElement(billing_address, 'BV.120_Land').text = 'CH'

    payment_conditions = et.SubElement(invoice_header, 'I.H.080_Zahlungsbedingungen')
    et.SubElement(payment_conditions, 'BV.010_Zahlungsbedingungen').text = 'Faelligkeitsdatum'
    et.SubElement(payment_conditions, 'BV.020_Zahlungsbedingungen_Zusatzwert').text = str(get_due_date(
        get_date_time_from_json(
            json_bill['commission']['date'],
            json_bill['commission']['time']), json_bill['commission']['deadline_days']))

    vat_information = et.SubElement(invoice_header, 'I.H.140_MwSt._Informationen')
    et.SubElement(vat_information, 'BV.010_Eingetragener_Name_des_Lieferanten').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(vat_information, 'BV.020_MwSt_Nummer_des_Lieferanten').text = json_bill['commission']['contractor'][
        'company_id']


def get_date_time_from_json(date_json, time_json):
    return datetime.datetime(year=int(date_json['year']), month=int(date_json['month']), day=int(date_json['day']),
                             hour=int(time_json['hour']), minute=int(time_json['minute']),
                             second=int(time_json['second']))


def get_due_date(date_of_issue, deadline_days):
    return date_of_issue + datetime.timedelta(days=int(deadline_days))
