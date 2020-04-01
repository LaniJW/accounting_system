from pprint import pprint

from absl import app

import ftp.connection_manager
import util.config
import util.status_output
from util import bill_format, status_output

config_path = '../config.toml'


def main(argv):
    config = util.config.load_config(config_path)

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
            cs.retrbinary(f'RETR {filename}', lambda bill: use_bill(bill, filename))


def use_bill(bill, filename):
    bill = bill.decode('utf-8').replace('\r\n', '\n')

    format_intact = bill_format.check_bill_format(bill)
    if format_intact:
        json_bill = jsonify_bill(bill)
        print(bill + '\n')
        pprint(json_bill)
    else:
        status_output.warning_message(
            f'File {filename} was not processed because of some format errors. Please see errors above to fix issue.')


def jsonify_bill(bill):
    lines = bill.split('\n')
    info = {}
    for i, line in enumerate(lines):
        sections = line.split(';')

        if len(line) == 0:
            continue

        if i == 0:
            # Adds general data about commission.
            info['title'] = sections[0]
            info['commission'] = {
                'name': sections[1],
                'location': sections[2],
                'date': sections[3],
                'time': sections[4],
                'deadline': sections[5],
            }
        elif i == 1:
            # Adds data about the contractor.
            if not info['commission']:
                util.status_output.fatal_message('No commission data available to add client and contractor')
                exit()
            info['commission']['contractor'] = {
                'company_name': sections[2],
                'contact_name': sections[3],
                'email': sections[7],
                'address': {
                    'street': sections[4],
                    'city': sections[5]
                }
            }
        elif i == 2:
            # Adds data about the client.
            if not info['commission']:
                util.status_output.fatal_message('No commission data available to add client and contractor')
                exit()
            info['commission']['client'] = {
                'company_name': sections[2],
                'address': {
                    'street': sections[3],
                    'city': sections[4]
                }
            }
        else:
            if 'items' not in info:
                info['items'] = []
            item = {}
            for j, section in enumerate(sections):
                if j == 1:
                    item['id'] = section
                elif j == 2:
                    item['description'] = section
                elif j == 3:
                    item['amount'] = section
                elif j == 4:
                    item['price_per_item'] = section
                elif j == 5:
                    item['price_total'] = section
                elif j == 6:
                    item['tax'] = section
            info['items'].append(item)
    return info


if __name__ == '__main__':
    app.run(main)
