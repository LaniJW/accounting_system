import logging

import coloredlogs
from absl import app

import ftp.connection_manager
import parse.json
import parse.txt
import parse.xml
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
            cs.retrbinary(f'RETR {filename}',
                          lambda bill: use_bill(bill, filename))


def use_bill(bill, filename):
    bill = bill.decode('utf-8').replace('\r\n', '\n')

    format_intact = util.bill_format.check_bill_format(bill)
    if format_intact:
        json_bill = parse.json.jsonify_bill(bill)
        logging.info('Parsing to JSON done.')
        xml_bill = parse.xml.xmlify_bill(json_bill, config)
        logging.info('Parsing to XML done.')
        txt_bill = parse.txt.txtify_bill(json_bill)
        logging.info('Parsing to txt done.')
    else:
        logging.warning(
            f'File {filename} was not processed because of some format errors. Please see errors above to fix issue.')


if __name__ == '__main__':
    app.run(main)
