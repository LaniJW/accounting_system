import io
import logging
import os
import time
from zipfile import ZipFile

import coloredlogs
from absl import app

import ftp.connection_manager
import mail.post
import parse.json
import parse.txt
import parse.xml
import util.bill_format
import util.config
import util.ftp_folders

config_path = '../config.toml'
config = util.config.load_config(config_path)

logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(module)s:%(lineno)d %(levelname)s - %(message)s')
coloredlogs.install()

COMPANY_SUBDIR = 'AP17bWagner'
RECEIPT_QUERY_DELAY = 20


def main(_):
    if not util.config.check_fields(config):
        exit()
    else:
        logging.info('Configuration intact. Proceeding.')
    remove_accounting_server_files()

    cs = ftp.connection_manager.create_customer_server_session(config)

    # Change to own billing directory
    cs.cwd(util.ftp_folders.get_out_folder(COMPANY_SUBDIR))
    # Fetch all bill files from directory and call use_bill callback
    logging.info('Searching for bills.')
    bills = fetch_bills(cs.nlst(), cs)

    if len(bills) < 1:
        logging.info('No bills found.')
    for bill in bills:
        logging.info('Working with bill "{}"'.format(bill['filename']))
        use_bill(bill['file'], bill['filename'])

    cs.close()


def fetch_bills(files, cs):
    bills = []
    for filename in files:
        file_ending = filename.split('.')[len(filename.split('.')) - 1]
        if filename != '.' and filename != '..' and file_ending == 'data':
            logging.info(f'Found data file {filename}.')
            with io.BytesIO() as buffer_io:
                cs.retrbinary(f'RETR {filename}', buffer_io.write)
                bills.append(
                    {'file': buffer_io.getvalue(), 'filename': filename})
                cs.delete(filename)
    return bills


def use_bill(bill, filename):
    bill = bill.decode('utf-8').replace('\r\n', '\n')

    format_intact = util.bill_format.check_bill_format(bill)
    if format_intact:
        logging.info(f'Invoice format check passed. Moving on with processing.')
        json_bill = parse.json.jsonify_bill(bill)
        logging.info('Parsing to JSON done.')
        xml_bill = parse.xml.xmlify_bill(json_bill, config)
        logging.info('Parsing to XML done.')
        txt_bill = parse.txt.txtify_bill(json_bill)
        logging.info('Parsing to txt done.')

        file_uploaded = False
        working = True
        while working:
            if not file_uploaded:
                upload_bills(json_bill, xml_bill, txt_bill)
                logging.info('Uploaded bills.')
                file_uploaded = True

            logging.info(
                f'Waiting for {RECEIPT_QUERY_DELAY} seconds to query receipt.')
            time.sleep(RECEIPT_QUERY_DELAY)

            if file_uploaded:
                logging.info('Checking for generated receipt.')
                receipt, receipt_filename = query_receipt()
                if receipt:
                    use_receipt(json_bill, receipt, txt_bill, receipt_filename)
                    working = False
    else:
        logging.warning(
            f'File {filename} was not processed because of some format errors. Please see errors above to fix issue.')


def upload_bills(json_bill, xml_bill, txt_bill):
    client_id = json_bill['commission']['contractor']['client_id']
    bill_nr = json_bill['bill_nr']

    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_in_folder(COMPANY_SUBDIR))

    xml_bill_file = io.BytesIO(xml_bill.encode())
    ps.storbinary(f'STOR {client_id}_{bill_nr}_invoice.xml', xml_bill_file)

    txt_bill_file = io.BytesIO(txt_bill.encode())
    ps.storbinary(f'STOR {client_id}_{bill_nr}_invoice.txt', txt_bill_file)

    ps.close()


def query_receipt():
    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_out_folder(COMPANY_SUBDIR))

    for filename in ps.nlst():
        if filename.startswith('quittungsfile') and filename.endswith('.txt'):
            logging.info(f'Receipt file {filename} found.')
            with io.BytesIO() as buffer_io:
                ps.retrbinary(f'RETR {filename}', buffer_io.write)
                ps.close()
                return buffer_io.getvalue(), filename
    return None, None


def use_receipt(json_bill, receipt, txt_bill, gen_filename):
    receipt_filename = gen_filename
    bill_filename, zip_filename = generate_temporary_final_filenames(json_bill)

    with open(receipt_filename, 'wb') as f:
        f.write(receipt)
    with open(bill_filename, 'w') as f:
        f.write(txt_bill)

    with ZipFile(zip_filename, 'w') as zip:
        zip.write(bill_filename)
        zip.write(receipt_filename)
        zip.close()
    logging.info(f'Wrote temporary zip file "{zip_filename}".')

    # Upload zip to customer FTP server.
    cs = ftp.connection_manager.create_customer_server_session(config)
    cs.cwd(util.ftp_folders.get_in_folder(COMPANY_SUBDIR))
    with open(zip_filename, 'rb') as f:
        cs.storbinary(f'STOR {zip_filename}', f)
    cs.close()
    logging.info('ZIP file uploaded to customer server.')
    # Send zip per email
    with open(zip_filename, 'rb') as f:
        mail.post.send_processing_mail(json_bill, zip_filename, f.read(),
                                       gen_filename, config)
    logging.info('Email sent.')

    os.remove(receipt_filename)
    os.remove(bill_filename)
    os.remove(zip_filename)
    logging.info(f'Removed temporary files.')

    # Delete old files from accounting server
    remove_accounting_server_files()


def generate_temporary_final_filenames(json_bill):
    client_id = json_bill['commission']['contractor']['client_id']
    bill_nr = json_bill['bill_nr']
    return f'{client_id}_{bill_nr}_invoice.txt', f'{client_id}_{bill_nr}.zip'


def remove_accounting_server_files():
    logging.info(
        'Removed any old/new files from accounting server for clean state.')
    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_in_folder(COMPANY_SUBDIR))
    for file in ps.nlst():
        if file == 'invoice.txt' or file == 'invoice.xml':
            ps.delete(file)
    ps.close()
    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_out_folder(COMPANY_SUBDIR))
    for file in ps.nlst():
        if file.startswith('quittungsfile') and file.endswith('.txt'):
            ps.delete(file)
    ps.close()


if __name__ == '__main__':
    app.run(main)
