import io
import logging
import os
import time
import uuid
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

accounting_server_blocked = False
file_uploaded = False
done = False


def main(_):
    # TODO(laniw): Check if config has all required fields and values
    # TODO(laniw): Remove any preexisting files on accounting server or customer in folder.

    cs = ftp.connection_manager.create_customer_server_session(config)

    # Change to own billing directory
    cs.cwd(util.ftp_folders.get_out_folder(COMPANY_SUBDIR))
    # Fetch all bill files from directory and call use_bill callback
    bills = fetch_bills(cs.nlst(), cs)

    for bill in bills:
        use_bill(bill['file'], bill['filename'])

    cs.close()


def fetch_bills(files, cs):
    bills = []
    logging.info('Searching for .data files.')
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
    global accounting_server_blocked
    global file_uploaded

    bill = bill.decode('utf-8').replace('\r\n', '\n')

    format_intact = util.bill_format.check_bill_format(bill)
    if format_intact:
        json_bill = parse.json.jsonify_bill(bill)
        logging.info('Parsing to JSON done.')
        xml_bill = parse.xml.xmlify_bill(json_bill, config)
        logging.info('Parsing to XML done.')
        txt_bill = parse.txt.txtify_bill(json_bill)
        logging.info('Parsing to txt done.')
        while True:
            if not accounting_server_blocked and not file_uploaded:
                upload_bills(xml_bill, txt_bill)
                logging.info('Uploaded bills.')
                accounting_server_blocked = True
                file_uploaded = True

            if file_uploaded:
                logging.info('Checking for generated receipt.')
                query_receipt(json_bill, txt_bill)

            if not done:
                logging.info(
                    f'Waiting for {RECEIPT_QUERY_DELAY} seconds to requery receipt.')
                time.sleep(RECEIPT_QUERY_DELAY)
            else:
                logging.info(
                    'Receipt file processing done. Exiting query loop.')
                break
    else:
        logging.warning(
            f'File {filename} was not processed because of some format errors. Please see errors above to fix issue.')


def upload_bills(xml_bill, txt_bill):
    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_in_folder(COMPANY_SUBDIR))

    temp_filename = 'temp_{}'.format(uuid.uuid1())

    temp_file_object = get_file_object(xml_bill, temp_filename, 'wb')
    ps.storbinary('STOR invoice.xml', temp_file_object)
    temp_file_object.close()

    temp_file_object = get_file_object(txt_bill, temp_filename, 'w')
    ps.storbinary('STOR invoice.txt', temp_file_object)
    temp_file_object.close()

    os.remove(temp_filename)

    ps.close()


def query_receipt(json_bill, txt_bill):
    global accounting_server_blocked
    global file_uploaded

    ps = ftp.connection_manager.create_accounting_server_session(config)
    ps.cwd(util.ftp_folders.get_out_folder(COMPANY_SUBDIR))

    for filename in ps.nlst():
        if filename.startswith('quittungsfile') and filename.endswith('.txt'):
            logging.info(f'Receipt file {filename} found.')
            with io.BytesIO() as buffer_io:
                ps.retrbinary(f'RETR {filename}', buffer_io.write)
                receipt = buffer_io.getvalue()
            use_receipt(json_bill, receipt, txt_bill, filename)
            break


def use_receipt(json_bill, receipt, txt_bill, gen_filename):
    global accounting_server_blocked
    global file_uploaded
    global done

    client_id = json_bill['commission']['contractor']['client_id']
    bill_nr = json_bill['bill_nr']
    # TODO(laniw): What name are the files supposed to have?
    receipt_filename = f'quittung{client_id}_{bill_nr}.txt'
    bill_filename = f'invoice{client_id}_{bill_nr}.txt'
    zip_filename = f'{client_id}_{bill_nr}.zip'

    with open(receipt_filename, 'wb') as f:
        f.write(receipt)
    logging.info(f'Wrote temporary receipt file "{receipt_filename}".')
    with open(bill_filename, 'w') as f:
        f.write(txt_bill)
    logging.info(f'Wrote temporary bill file "{bill_filename}".')

    zip_obj = ZipFile(zip_filename, 'w')
    zip_obj.write(bill_filename)
    zip_obj.write(receipt_filename)
    zip_obj.close()
    logging.info(f'Wrote temporary zip file "{zip_filename}".')

    # Upload zip to customer FTP server.
    cs = ftp.connection_manager.create_customer_server_session(config)
    cs.cwd(util.ftp_folders.get_in_folder(COMPANY_SUBDIR))
    temp_file_object = open(zip_filename, 'rb')
    cs.storbinary(f'STOR {zip_filename}', temp_file_object)
    cs.close()
    logging.info('ZIP file uploaded to customer server.')
    # Send zip per email
    mail.post.send_processing_mail(json_bill, zip_filename,
                                   open(zip_filename, 'rb').read(),
                                   gen_filename,
                                   config)
    logging.info('Email sent.')

    os.remove(receipt_filename)
    os.remove(bill_filename)
    # TODO(laniw): Fix this: os.remove(zip_filename)
    logging.info(f'Removed temporary files.')

    logging.info('Done processing bills.')
    # Delete old files on payment processing server
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

    # Reset flow controlling booleans
    accounting_server_blocked = False
    file_uploaded = False
    done = True


def get_file_object(content, filename, writemode):
    with open(filename, writemode) as f:
        f.write(content)

    return open(filename, 'rb')


if __name__ == '__main__':
    app.run(main)
