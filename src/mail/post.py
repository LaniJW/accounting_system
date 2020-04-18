import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

msession = None


def send_processing_mail(json_bill, invoice_txt, bill_txt, config):
    mail = setup_defaults(config)
    mail['Subject'] = 'Erfolgte Verarbeitung Rechnung {}'.format(
        json_bill['bill_nr'])
    mail.attach(MIMEText(generate_message(), 'plain'))

    create_smtp_session(config)
    send_mail(config, mail.as_string())
    close_smtp_session()


def generate_message():
    # TODO(laniw): Add appropriate message with formatted content.
    return 'This is a test'


def setup_defaults(config):
    mail = MIMEMultipart()
    mail['From'] = config['email']['sender']['email']
    mail['To'] = config['email']['recipient']['email']

    return mail


def create_smtp_session(config):
    global msession

    msession = smtplib.SMTP(config['email']['sender']['smtp']['server'],
                            config['email']['sender']['smtp']['port'])
    msession.starttls()
    msession.login(config['email']['sender']['email'],
                   config['email']['sender']['pw'])


def send_mail(config, text):
    msession.sendmail(config['email']['sender']['email'],
                      config['email']['recipient']['email'], text)
    logging.info('Email sent.')


def close_smtp_session():
    msession.quit()
