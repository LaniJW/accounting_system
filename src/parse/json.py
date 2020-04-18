import logging


def jsonify_bill(bill):
    lines = bill.split('\n')
    info = {}
    for i, line in enumerate(lines):
        sections = line.split(';')

        if len(line) == 0:
            continue

        if i == 0:
            # Adds general data about commission.
            info['bill_nr'] = sections[0].split('_')[1]
            info['commission'] = {
                'number': sections[1].split('_')[1],
                'location': sections[2],
                'date': {
                    'year': sections[3].split('.')[2],
                    'month': sections[3].split('.')[1],
                    'day': sections[3].split('.')[0]
                },
                'time': {
                    'hour': sections[4].split(':')[0],
                    'minute': sections[4].split(':')[1],
                    'second': sections[4].split(':')[2]
                },
                'deadline_days': sections[5].split('_')[1]
            }
        elif i == 1:
            # Adds data about the contractor.
            if not info['commission']:
                logging.warning(
                    'No commission data available to add client and contractor')
                exit()
            info['commission']['contractor'] = {
                'company_name': sections[2],
                'company_id': sections[6],
                'contact_name': sections[3],
                'email': sections[7],
                'client_id': sections[1],
                'address': {
                    'street': get_street_number_dict(sections[4]),
                    'city': get_plz_city_dict(sections[5])
                }
            }
        elif i == 2:
            # Adds data about the client.
            if not info['commission']:
                logging.warning(
                    'No commission data available to add client and contractor')
                exit()
            info['commission']['client'] = {
                'company_name': sections[2],
                'client_id': sections[1],
                'address': {
                    'street': get_street_number_dict(sections[3]),
                    'city': get_plz_city_dict(sections[4])
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
                    item['tax'] = section.split('_')[1]
            info['items'].append(item)
    return info


def get_street_number_dict(street_number_compound):
    sections = street_number_compound.split(' ')
    number = sections[-1]
    sections.remove(number)
    street = ' '.join(sections)
    return {
        'street': street,
        'number': number
    }


def get_plz_city_dict(plz_city_compound):
    sections = plz_city_compound.split(' ')
    plz = sections[0]
    sections.remove(plz)
    city = ' '.join(sections)
    return {
        'city': city,
        'plz': plz
    }
