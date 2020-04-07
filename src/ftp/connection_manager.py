import ftplib
import logging

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
        logging.error('No customer server session to close.', line=util.get_file_linenumber())
        return False
    else:
        customer_server_session.quit()
        return True


def close_accounting_server_session():
    if not accounting_server_session:
        logging.critical('No accounting server session to close.', line=util.get_file_linenumber())
        return False
    else:
        accounting_server_session.quit()
        return True


def create_session(c):
    return ftplib.FTP(c['address'], c['user'], c['pw'])
