import logging

import toml


def load_config(path):
    try:
        conf = toml.load(path)
    except FileNotFoundError:
        logging.warning(
            'Configuration file was not found at specified path: {}'.format(
                path))
        exit()
    return conf


def check_fields(config):
    config_intact = True
    continued_process = 'Program will not run.'

    client_server_config_intact = True
    if not config['client_server']:
        config_intact = False
        client_server_config_intact = False
        logging.fatal(
            f'No client server configuration found. {continued_process}')
    if client_server_config_intact and not config['client_server']['address']:
        config_intact = False
        logging.fatal(f'No client server address found. {continued_process}')
    if client_server_config_intact and not config['client_server']['user']:
        config_intact = False
        logging.fatal(f'No client server user found. {continued_process}')
    if client_server_config_intact and not config['client_server']['pw']:
        config_intact = False
        logging.fatal(f'No client server user found. {continued_process}')

    accounting_server_config_intact = True
    if not config['accounting_server']:
        config_intact = False
        accounting_server_config_intact = False
        logging.fatal(
            f'No client server configuration found. {continued_process}')
    if accounting_server_config_intact and not config['accounting_server'][
        'address']:
        config_intact = False
        logging.fatal(f'No client server address found. {continued_process}')
    if accounting_server_config_intact and not config['accounting_server'][
        'user']:
        config_intact = False
        logging.fatal(f'No client server user found. {continued_process}')
    if accounting_server_config_intact and not config['accounting_server'][
        'pw']:
        config_intact = False
        logging.fatal(f'No client server user found. {continued_process}')

    data_config_intact = True
    if not config['data']:
        config_intact = False
        data_config_intact = False
        logging.fatal(f'No data configuration found. {continued_process}')
    if data_config_intact and not config['data']['email_address']:
        config_intact = False
        logging.fatal(f'No email data configuration found. {continued_process}')

    email_config_intact = True
    email_sender_config_intact = True
    email_sender_smtp_config_intact = True
    if not config['email']:
        config_intact = False
        email_config_intact = False
        logging.fatal(f'No email configuration found. {continued_process}')
    if email_config_intact and not config['email']['sender']:
        config_intact = False
        email_sender_config_intact = False
        logging.fatal(
            f'No email sender configuration found. {continued_process}')
    if email_sender_config_intact and not config['email']['sender']['email']:
        config_intact = False
        logging.fatal(
            f'No sender email configuration found. {continued_process}')
    if email_sender_config_intact and not config['email']['sender']['pw']:
        config_intact = False
        logging.fatal(
            f'No sender password configuration found. {continued_process}')
    if email_sender_config_intact and not config['email']['sender']['smtp']:
        config_intact = False
        email_sender_smtp_config_intact = False
        logging.fatal(f'No smtp email configuration found. {continued_process}')
    if email_sender_smtp_config_intact and not \
    config['email']['sender']['smtp']['server']:
        config_intact = False
        logging.fatal(
            f'No smtp server configuration found. {continued_process}')
    if email_sender_smtp_config_intact and not \
    config['email']['sender']['smtp']['port']:
        config_intact = False
        logging.fatal(
            f'No smtp server configuration found. {continued_process}')

    return config_intact
