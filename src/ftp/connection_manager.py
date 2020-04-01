import ftplib

from util import status_output

customer_server_session = None
accounting_server_session = None


def create_customer_server_session(config):
    global customer_server_session
    customer_server_session = create_session(config['client_server'])
    return customer_server_session


def create_accounting_server_session(config):
    global accounting_server_session
    accounting_server_session = create_session(config['accounting_server'])
    return accounting_server_session


def close_customer_server_session():
    if not customer_server_session:
        status_output.error_message('No customer server session to close.')
        return False
    else:
        customer_server_session.quit()
        return True


def close_accounting_server_session():
    if not accounting_server_session:
        status_output.error_message('No accounting server session to close.')
        return False
    else:
        accounting_server_session.quit()
        return True


def create_session(c):
    return ftplib.FTP(c['address'], c['user'], c['pw'])
