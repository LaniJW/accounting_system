import ftplib


def create_customer_server_session(config):
    return create_session(config['client_server'])


def create_accounting_server_session(config):
    return create_session(config['accounting_server'])


def create_session(c):
    return ftplib.FTP(c['address'], c['user'], c['pw'])
