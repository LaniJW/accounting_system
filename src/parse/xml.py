import xml.etree.cElementTree as et

import parse.util

CONFIG = None


def xmlify_bill(json_bill, config):
    global CONFIG

    root = et.Element('Invoice', version='3.1', doctype='ETS Invoice')
    CONFIG = config

    add_invoice_header(root, json_bill)
    add_invoice_detail(root, json_bill)
    add_invoice_summary(root, json_bill)

    tree = et.ElementTree(root)
    tree.write('bill.xml')
    return et.tostring(root, 'utf8')


def add_invoice_header(root, json_bill):
    invoice_header = et.SubElement(root, 'Invoice_Header')

    basedata = et.SubElement(invoice_header, 'I.H.010_Basisdaten')
    et.SubElement(basedata, 'BV.010_Rechnungsnummer').text = \
        json_bill['commission']['number']
    et.SubElement(basedata, 'BV.020_Rechnungsdatum').text = str(
        parse.util.get_date_time_from_json(json_bill['commission']['date'],
                                           json_bill['commission']['time']))
    et.SubElement(basedata, 'BV.030_Funktion_des_Dokuments').text = 'Original'
    et.SubElement(basedata, 'BV.040_Typ_des_Dokuments').text = 'Rechnung'
    et.SubElement(basedata,
                  'BV.050_Rechnungs_Endkennzeichen').text = 'vollstaendige Rechnung'
    et.SubElement(basedata, 'BV.060_Bestellnummer_des_Kaeufers')
    et.SubElement(basedata, 'BV.080_Waehrung').text = 'CHF'
    et.SubElement(basedata, 'BV.090_Sprache').text = 'de'

    client_identification = et.SubElement(invoice_header,
                                          'I.H.020_Einkaeufer_Identifikation')
    et.SubElement(client_identification,
                  'BV.010_Nr_Kaeufer_beim_Lieferanten').text = 'undef'
    et.SubElement(client_identification,
                  'BV.020_Nr_Kaeufer_beim_Kaeufer').text = \
        json_bill['commission']['contractor'][
            'client_id']
    et.SubElement(client_identification, 'BV.030_Nr_Kaeufer_bei_ETS').text = \
        json_bill['commission']['client'][
            'client_id']
    et.SubElement(client_identification,
                  'BV.035_Typ_der_Handelsplatz_ID').text = 'TPID'
    et.SubElement(client_identification, 'BV.040_Name1').text = \
        json_bill['commission']['client']['company_name']
    et.SubElement(client_identification, 'BV.100_PLZ').text = \
        json_bill['commission']['client']['address']['city'][
            'plz']
    et.SubElement(client_identification, 'BV.110_Stadt').text = \
        json_bill['commission']['client']['address']['city'][
            'city']
    et.SubElement(client_identification, 'BV.120_Land').text = 'CH'

    contractor_identification = et.SubElement(invoice_header,
                                              'I.H.030_Lieferanten_Identifikation')
    et.SubElement(contractor_identification,
                  'BV.010_Nr_Lieferant_beim_Kaeufer').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(contractor_identification,
                  'BV.030_Nr_Lieferant_bei_ETS').text = CONFIG['data'][
        'email_address']
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
    et.SubElement(billing_address, 'BV.040_Name1').text = \
        json_bill['commission']['client']['company_name']
    et.SubElement(billing_address, 'BV.100_PLZ').text = \
        json_bill['commission']['client']['address']['city']['plz']
    et.SubElement(billing_address, 'BV.110_Stadt').text = \
        json_bill['commission']['client']['address']['city']['city']
    et.SubElement(billing_address, 'BV.120_Land').text = 'CH'

    payment_conditions = et.SubElement(invoice_header,
                                       'I.H.080_Zahlungsbedingungen')
    et.SubElement(payment_conditions,
                  'BV.010_Zahlungsbedingungen').text = 'Faelligkeitsdatum'
    et.SubElement(payment_conditions,
                  'BV.020_Zahlungsbedingungen_Zusatzwert').text = str(
        parse.util.get_due_date(
            parse.util.get_date_time_from_json(
                json_bill['commission']['date'],
                json_bill['commission']['time']),
            json_bill['commission']['deadline_days']))

    vat_information = et.SubElement(invoice_header,
                                    'I.H.140_MwSt._Informationen')
    et.SubElement(vat_information,
                  'BV.010_Eingetragener_Name_des_Lieferanten').text = \
        json_bill['commission']['contractor']['company_name']
    et.SubElement(vat_information, 'BV.020_MwSt_Nummer_des_Lieferanten').text = \
        json_bill['commission']['contractor'][
            'company_id']


def add_invoice_detail(root, json_bill):
    invoice_detail = et.SubElement(root, 'Invoice_Detail')
    invoice_items = et.SubElement(invoice_detail, 'Invoice_Items')

    for item in json_bill['items']:
        basedata = et.SubElement(invoice_items, 'I.D.010_Basisdaten')
        et.SubElement(basedata, 'BV.010_Positions_Nr_in_der_Rechnung').text = \
            item['id']
        et.SubElement(basedata, 'BV.020_Artikel_Nr_des_Lieferanten').text = \
            item['id']
        et.SubElement(basedata, 'BV.070_Artikel_Beschreibung').text = item[
            'description']
        et.SubElement(basedata,
                      'BV.140_Abschlussdatum_der_Lieferung_Ausfuehrung').text = str(
            parse.util.get_date_time_from_json(json_bill['commission']['date'],
                                               json_bill['commission']['time']))

        price_and_amount = et.SubElement(invoice_items,
                                         'I.D.020_Preise_und_Mengen')
        et.SubElement(price_and_amount, 'BV.010_Verrechnete_Menge').text = item[
            'amount']
        et.SubElement(price_and_amount,
                      'BV.020_Mengeneinheit_der_verrechneten_Menge').text = 'BLL'
        et.SubElement(price_and_amount,
                      'BV.030_Verrechneter_Einzelpreis_des_Artikels').text = \
            item['price_per_item']
        et.SubElement(price_and_amount,
                      'BV.040_Waehrung_des_Einzelpreises').text = 'CHF'
        et.SubElement(price_and_amount,
                      'BV.070_Bestaetigter_Gesamtpreis_der_Position_netto').text = \
            item['price_total']
        et.SubElement(price_and_amount,
                      'BV.080_Bestaetigter_Gesamtpreis_der_Position_brutto').text = \
            item[
                'price_total']
        et.SubElement(price_and_amount,
                      'BV.090_Waehrung_des_Gesamtpreises').text = 'CHF'

        taxes = et.SubElement(invoice_items, 'I.D.030_Steuern')
        et.SubElement(taxes, 'BV.010_Funktion_der_Steuer').text = 'Steuer'
        et.SubElement(taxes,
                      'BV.020_Steuersatz_Kategorie').text = 'Standard Satz'
        et.SubElement(taxes, 'BV.030_Steuersatz').text = item['tax']
        et.SubElement(taxes, 'BV.040_Zu_versteuernder_Betrag').text = str(
            parse.util.get_total_price(json_bill['items']))
        et.SubElement(taxes, 'BV.050_Steuerbetrag').text = '0.00'


def add_invoice_summary(root, json_bill):
    invoice_summary = et.SubElement(root, 'Invoice_Summary')

    basedata = et.SubElement(invoice_summary, 'I.S.010_Basisdaten')
    et.SubElement(basedata, 'BV.010_Anzahl_der_Rechnungspositionen').text = str(
        len(json_bill['items']))
    et.SubElement(basedata,
                  'BV.020_Gesamtbetrag_der_Rechnung_exkl_MwSt_exkl_Ab_Zuschlag').text = str(
        parse.util.get_total_price(json_bill['items']))
    et.SubElement(basedata,
                  'BV.030_Waehrung_Gesamtbetrag_der_Rechnung_exkl_MwSt_exkl_Ab_Zuschlag').text = 'CHF'
    et.SubElement(basedata,
                  'BV.040_Gesamtbetrag_der_Rechnung_exkl_MwSt_inkl_Ab_Zuschlag').text = str(
        parse.util.get_total_price(json_bill['items']))
    et.SubElement(basedata,
                  'BV.050_Waehrung_Gesamtbetrag_der_Rechnung_exkl_MwSt_inkl_Ab_Zuschlag').text = 'CHF'
    et.SubElement(basedata, 'BV.060_Steuerbetrag').text = '0.00'
    et.SubElement(basedata, 'BV.070_Waehrung_des_Steuerbetrags').text = 'CHF'
    et.SubElement(basedata,
                  'BV.080_Gesamtbetrag_der_Rechnung_inkl_MwSt_inkl_Ab_Zuschlag').text = str(
        parse.util.get_total_price(json_bill['items']))
    et.SubElement(basedata,
                  'BV.090_Waehrung_Gesamtbetrag_der_Rechnung_inkl_MwSt_inkl_Ab_Zuschlag').text = 'CHF'

    tax_breakdown = et.SubElement(invoice_summary,
                                  'I.S.020_Aufschluesselung_der_Steuern')
    et.SubElement(tax_breakdown, 'BV.010_Funktion_der_Steuer').text = 'Steuer'
    et.SubElement(tax_breakdown,
                  'BV.020_Steuersatz_Kategorie').text = 'Standard Satz'
    et.SubElement(tax_breakdown, 'BV.030_Steuersatz').text = 'MWST_0.00%'
    et.SubElement(tax_breakdown, 'BV.040_Zu_versteuernder_Betrag').text = str(
        parse.util.get_total_price(json_bill['items']))
    et.SubElement(tax_breakdown, 'BV.050_Steuerbetrag').text = '0.00'
    et.SubElement(tax_breakdown, 'BV.055_Waehrung_Steuerbetrag').text = 'CHF'
