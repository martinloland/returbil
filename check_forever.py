import argparse
import datetime as dt
import os
import pickle
import string
import time

import requests
from bs4 import BeautifulSoup as soup4

from private import PUSHOVER_USER_KEY_MARTIN as PUSHOVER_USER_KEY
from private import RETURBIL_PUSH_TOKEN
from push import send_push

SUCCESSFUL_REQUEST_CODE = 200
WEBPAGE = 'http://returbil.no/freecar.asp'
BGCOLORS = ['#DEE3E7', '#EFEFEF']
DATABASE = 'database.pickle'


def log_add_line(text):
    with open('log.txt', 'a+') as f:
        f.write(str(dt.datetime.now()) + ' ' + text + "\r")


def database_list():
    if os.path.isfile(DATABASE):
        with open(DATABASE, 'rb') as f:
            return pickle.load(f)
    else:
        return []


def add_id(id):
    if os.path.isfile(DATABASE):
        with open(DATABASE, 'rb') as f:
            old_ids = pickle.load(f)
        with open(DATABASE, 'wb') as f:
            old_ids.append(id)
            pickle.dump(old_ids, f, pickle.HIGHEST_PROTOCOL)
        log_add_line('Added {}'.format(id))
    else:
        with open(DATABASE, 'wb') as f:
            pickle.dump([id], f, pickle.HIGHEST_PROTOCOL)
        log_add_line('Created database')
        log_add_line('Added {}'.format(id))


def check(fra_by, til_by, token, user, update_db=False):
    log_add_line('Checked for cars {} -> {}'.format(fra_by, til_by))
    fra_by = fra_by.lower().replace('\xf8', 'o')
    til_by = til_by.lower().replace('\xf8', 'o')
    r = requests.get(WEBPAGE)
    if r.status_code is SUCCESSFUL_REQUEST_CODE:
        soup = soup4(r.content, 'html.parser')
        for color in BGCOLORS:
            lines = soup.find_all('tr', {'height': '', 'bgcolor': color})
            for line in lines:
                cols = line.contents
                url = 'http://returbil.no/' + line.find('a', href=True)['href']
                id = str(cols[1].string)
                dtg = cols[3].string
                fra = cols[5].string.lower().replace('\xf8', 'o')
                til = cols[7].string.lower().replace('\xf8', 'o')
                if id not in database_list():
                    if update_db:
                        add_id(id)
                    else:
                        if fra_by in fra and til_by in til:
                            send_push(title='Nytt treff på returbil',
                                      message='Fra: {}\nTil: {}\nLedig fra: {}'
                                      .format(string.capwords(fra),
                                              string.capwords(til),
                                              string.capwords(dtg)),
                                      url=url,
                                      token=token,
                                      user=user)
                            msg = 'Sent id {} to phone'.format(id)
                            log_add_line(msg)
                            print(msg)


def get_wanted():
    wanted = []
    with open('wanted.txt', 'r') as f:
        for line in f.readlines():
            contents = line.rstrip().split(',')
            if contents:
                fra = contents[0]
                til = contents[1]
                usr = contents[2]
                if usr == '':
                    usr = PUSHOVER_USER_KEY
                wanted.append({'from_city': fra,
                               'to_city': til,
                               'usr': usr})
    return wanted


def main():
    parser = argparse.ArgumentParser(
        description='Check returbil.no for cars')
    parser.add_argument(
        '-from_city',
        metavar='FROM',
        type=str,
        help='The city to travel from (default from file)')
    parser.add_argument(
        '-to_city',
        metavar='TO',
        type=str,
        help='The city to travel to (default from file)')
    parser.add_argument(
        '-i',
        metavar='INTERVAL',
        type=int,
        default=60,
        help='interval time for check in seconds (default 60)')
    parser.add_argument(
        '-app',
        metavar='APP_TOKEN',
        type=str,
        help='the pushover app token (default secret)')
    parser.add_argument(
        '-usr',
        metavar='USER_TOKEN',
        type=str,
        help='the pushover user token (default secret)')
    parser.add_argument(
        '--fromfile',
        action="store_true",
        help='set to load cities from wanted.txt',
        )
    args = parser.parse_args()

    if not args.app:
        app_token = RETURBIL_PUSH_TOKEN
    else:
        app_token = args.app

    wanted = []
    if not args.fromfile:
        if not args.usr:
            user = PUSHOVER_USER_KEY
        else:
            user = args.usr
        wanted.append({'from_city': args.from_city,
                       'to_city': args.to_city,
                       'usr': user})

    last_check = dt.datetime.now() - dt.timedelta(days=1)
    while True:
        if dt.datetime.now() - last_check > dt.timedelta(seconds=args.i):
            if args.fromfile:
                wanted = get_wanted()
            for trip in wanted:
                try:
                    check(fra_by=trip['from_city'],
                          til_by=trip['to_city'],
                          token=app_token,
                          user=trip['usr'])
                except Exception as e:
                    send_push(title='Returbil exception',
                              message=str(e),
                              token=app_token,
                              user=PUSHOVER_USER_KEY)
                    log_add_line('Exception: ' + str(e))
                    time.sleep(60 * 3)
                    continue
            check(fra_by='None',
                  til_by='None',
                  token='None',
                  user='None',
                  update_db=True)
            last_check = dt.datetime.now()


if __name__ == "__main__":
    main()
