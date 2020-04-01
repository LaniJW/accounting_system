import toml

import util.status_output


def load_config(path):
    try:
        conf = toml.load(path)
    except FileNotFoundError:
        util.status_output.fatal_message('Configuration file was not found at specified path: {}'.format(path))
        exit()
    return conf
