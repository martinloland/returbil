import argparse
import datetime as dt
import os
import pickle
import string

import requests
from bs4 import BeautifulSoup as soup4

from private import RETURBIL_PUSH_TOKEN
from private import PUSHOVER_USER_KEY_MARTIN as PUSHOVER_USER_KEY
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


def check(fra_by, til_by, token, user):
    log_add_line('Checked for cars {} -> {}'.format(fra_by, til_by))
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
                fra = cols[5].string.lower()
                til = cols[7].string.lower()
                if '\xf8' in fra:
                    fra = fra.replace('\xf8', 'o')
                if '\xf8' in til:
                    til = til.replace('\xf8', 'o')
                if id not in database_list():
                    add_id(id)
                    if fra_by.lower() in fra and til_by.lower() in til:
                        send_push(title='Nytt treff på returbil',
                                  message='Fra: {}\nTil: {}\nLedig fra: {}'
                                  .format(string.capwords(fra),
                                          string.capwords(til),
                                          string.capwords(dtg)),
                                  url=url,
                                  token=token,
                                  user=user)
                        print('Sent push notification to your phone')


def main(args=None):
    parser = argparse.ArgumentParser(
        description='Check returbil.no for cars')
    parser.add_argument(
        'from_city',
        metavar='FROM',
        type=str,
        help='The city to travel from')
    parser.add_argument(
        'to_city',
        metavar='TO',
        type=str,
        help='The city to travel to')
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

    args = parser.parse_args()
    if not args.app:
        args.app = RETURBIL_PUSH_TOKEN
    if not args.usr:
        args.usr = PUSHOVER_USER_KEY

    last_check = dt.datetime.now() - dt.timedelta(days=1)
    while True:
        if dt.datetime.now() - last_check > dt.timedelta(seconds=args.i):
            check(fra_by=args.from_city,
                  til_by=args.to_city,
                  token=args.app,
                  user=args.usr)
            last_check = dt.datetime.now()


if __name__ == "__main__":
    main()
