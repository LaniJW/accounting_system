import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

msession = None


def send_processing_mail(json_bill, zip_filename, zip_file, gen_filename,
                         config):
    mail = setup_defaults(config, json_bill)
    mail['Subject'] = 'Erfolgte Verarbeitung Rechnung {}'.format(
        json_bill['bill_nr'])
    mail.attach(
        MIMEText(generate_message(json_bill, gen_filename, config), 'plain'))
    mail.attach(MIMEApplication(zip_file, Name=zip_filename))

    create_smtp_session(config)
    send_mail(config, json_bill, mail.as_string())
    close_smtp_session()


def generate_message(json_bill, gen_filename, config):
    address_line = 'Sehr geehrter {}'.format(
        json_bill['commission']['contractor']['contact_name'])
    message = 'Am {} um {} Uhr wurde die erfolgreiche Bearbeitung der Rechnung {} vom Zahlungssystem "{}" gemeldet.'.format(
        get_date_from_filename(gen_filename),
        get_time_from_filename(gen_filename), json_bill['bill_nr'],
        config['accounting_server']['address'])
    # TODO(laniw): Shouldn't this company name be something dynamic instead of "Firma_X"?
    greetings = 'Mit Freundlichen Grüssen\n\nLani Wagner\nFirma_X'
    return f'{address_line}\n\n{message}\n\n{greetings}'


def setup_defaults(config, json_bill):
    mail = MIMEMultipart()
    mail['From'] = config['email']['sender']['email']
    mail['To'] = json_bill['commission']['contractor']['email']

    return mail


def create_smtp_session(config):
    global msession

    msession = smtplib.SMTP(config['email']['sender']['smtp']['server'],
                            config['email']['sender']['smtp']['port'])
    msession.starttls()
    msession.login(config['email']['sender']['email'],
                   config['email']['sender']['pw'])


def send_mail(config, json_bill, text):
    msession.sendmail(config['email']['sender']['email'],
                      json_bill['commission']['contractor']['email'], text)


def close_smtp_session():
    msession.quit()


def get_date_from_filename(filename):
    scrunched_date = filename[13:28].split('_')[0]
    year = scrunched_date[0:4]
    month = scrunched_date[4:6]
    day = scrunched_date[6:]
    return f'{day}.{month}.{year}'


def get_time_from_filename(filename):
    scrunched_time = filename[13:28].split('_')[1]
    hour = scrunched_time[0:2]
    minute = scrunched_time[2:4]
    second = scrunched_time[4:]
    return f'{hour}:{minute}:{second}'
