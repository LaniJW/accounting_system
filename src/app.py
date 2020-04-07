import datetime
import logging
import xml.etree.cElementTree as et
from pprint import pprint

import coloredlogs
import dicttoxml
from absl import app

import ftp.connection_manager
import util.bill_format
import util.config

config_path = '../config.toml'
config = util.config.load_config(config_path)

logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s')
coloredlogs.install()


def main(_):
    # TODO(laniw): Check if config has all required fields and values

    cs = ftp.connection_manager.create_customer_server_session(config)

    # Change to own billing directory
    cs.cwd('out/AP17bWagner/')
    # Fetch all bill files from directory and call use_bill callback
    fetch_bills(cs.nlst(), cs)

    ftp.connection_manager.close_customer_server_session()


def fetch_bills(files, cs):
    for filename in files:
        file_ending = filename.split('.')[len(filename.split('.')) - 1]
        if filename != '.' and filename != '..' and file_ending == 'data':
            cs.retrbinary(f'RETR {filename}', lambda bill: use_bill(bill, filename))


def use_bill(bill, filename):
    bill = bill.decode('utf-8').replace('\r\n', '\n')

    format_intact = util.bill_format.check_bill_format(bill)
    if format_intact:
        json_bill = jsonify_bill(bill)
        xml_bill = xmlify_bill(json_bill)
        pprint(xml_bill)
    else:
        logging.warning(
            f'File {filename} was not processed because of some format errors. Please see errors above to fix issue.')


def jsonify_bill(bill):
    lines = bill.split('\n')
    info = {}
    for i, line in enumerate(lines):
        sections = line.split(';')

        if len(line) == 0:
            continue

        if i == 0:
            # Adds general data about commission.
            info['title'] = sections[0]
            info['commission'] = {
                'name': sections[1],
                'location': sections[2],
                'date': {
                    'year': sections[3].split('.')[2],
                    'month': sections[3].split('.')[1],
                    'day': sections[3].split('.')[0]
                },
                'time': {
                    'hour': sections[4].split(':')[0],
                    'minute': sections[4].split(':')[1],
                    'second': sections[4].split(':')[2]
                },
                'deadline_days': sections[5].split('_')[1]
            }
        elif i == 1:
            # Adds data about the contractor.
            if not info['commission']:
                logging.warning('No commission data available to add client and contractor')
                exit()
            info['commission']['contractor'] = {
                'company_name': sections[2],
                'company_id': sections[6],
                'contact_name': sections[3],
                'email': sections[7],
                'client_id': sections[1],
                'address': {
                    'street': get_street_number_dict(sections[4]),
                    'city': get_plz_city_dict(sections[5])
                }
            }
        elif i == 2:
            # Adds data about the client.
            if not info['commission']:
                logging.warning('No commission data available to add client and contractor')
                exit()
            info['commission']['client'] = {
                'company_name': sections[2],
                'client_id': sections[1],
                'address': {
                    'street': get_street_number_dict(sections[3]),
                    'city': get_plz_city_dict(sections[4])
                }
            }
        else:
            if 'items' not in info:
                info['items'] = []
            item = {}
            for j, section in enumerate(sections):
                if j == 1:
                    item['id'] = section
                elif j == 2:
                    item['description'] = section
                elif j == 3:
                    item['amount'] = section
                elif j == 4:
                    item['price_per_item'] = section
                elif j == 5:
                    item['price_total'] = section
                elif j == 6:
                    item['tax'] = section
            info['items'].append(item)
    return info


def xmlify_bill(json_bill):
    root = et.Element('Invoice', version='3.1', doctype='ETS Invoice')

    invoice_header = et.SubElement(root, 'Invoice_Header')

    basedata = et.SubElement(invoice_header, 'I.H.010_Basisdaten')
    et.SubElement(basedata, 'BV.010_Rechnungsnummer').text = json_bill['commission']['name']
    et.SubElement(basedata, 'BV.020_Rechnungsdatum').text = get_date_time_from_json(json_bill['commission']['date'],
                                                                                    json_bill['commission']['time'])
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
    et.SubElement(client_identification, 'BV.040_Name1').text = json_bill['commission']['client']['client_name']
    et.SubElement(client_identification, 'BV.100_PLZ').text = json_bill['commission']['client']['address']['plz'][
        'plz']
    et.SubElement(client_identification, 'BV.110_Stadt').text = json_bill['commission']['client']['address']['city'][
        'city']
    et.SubElement(client_identification, 'BV.120_Land').text = 'CH'

    contractor_identification = et.SubElement(invoice_header, 'I.H.030_Lieferanten_Identifikation')
    et.SubElement(contractor_identification, 'BV.010_Nr_Lieferant_beim_Kaeufer').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(contractor_identification, 'BV.030_Nr_Lieferant_bei_ETS').text = config['data']['email_address']
    et.SubElement(contractor_identification, 'BV.040_Name1').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(contractor_identification, 'BV.070_Strasse').text = \
        json_bill['commission']['contractor']['address']['street']
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
    et.SubElement(payment_conditions, 'BV.020_Zahlungsbedingungen_Zusatzwert').text = get_due_date(
        get_date_time_from_json(
            json_bill['commission']['date'],
            json_bill['commission']['time']), json_bill['commission']['deadline_days'])

    vat_information = et.SubElement(invoice_header, 'I.H.140_MwSt._Informationen')
    et.SubElement(vat_information, 'BV.010_Eingetragener_Name_des_Lieferanten').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(vat_information, 'BV.020_MwSt_Nummer_des_Lieferanten').text = json_bill['commission']['contractor'][
        'company_id']

    # TODO(laniw): Add converters for invoice details and invoice summary.

    tree = et.ElementTree(root)
    tree.write('bill.xml')
    return dicttoxml.dicttoxml(json_bill)


def get_date_time_from_json(date_json, time_json):
    return datetime.datetime(year=date_json['year'], month=date_json['month'], day=date_json['day'],
                             hour=time_json['hour'],
                             minute=time_json['minute'], second=time_json['second'])


def get_due_date(date_of_issue, deadline_days):
    print(date_of_issue + datetime.timedelta(days=deadline_days))
    return date_of_issue + datetime.timedelta(days=deadline_days)


def get_street_number_dict(street_number_compound):
    sections = street_number_compound.split(' ')
    number = sections[-1]
    sections.remove(number)
    street = ' '.join(sections)
    return {
        'street': street,
        'number': number
    }


def get_plz_city_dict(plz_city_compound):
    sections = plz_city_compound.split(' ')
    plz = sections[0]
    sections.remove(plz)
    city = ' '.join(sections)
    return {
        'city': city,
        'plz': plz
    }


if __name__ == '__main__':
    app.run(main)
