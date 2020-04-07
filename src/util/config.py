import logging

import toml


def load_config(path):
    try:
        conf = toml.load(path)
    except FileNotFoundError:
        logging.warning('Configuration file was not found at specified path: {}'.format(path))
        exit()
    return conf
