import argparse
import asyncio
import os

from logger import Logger
from returbil import Returbil


def _set_up_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='This script scans http://returbil.no for desired trips.')

    parser.add_argument(
        '-usr', metavar='USER_KEY', type=str, help='Pushover user key')
    parser.add_argument(
        '-app', metavar='APP_TOKEN', type=str, help='Pushover app token')

    parser.add_argument(
        '--from-city', metavar='FROM', type=str, help='The city to travel from')
    parser.add_argument(
        '--to-city', metavar='TO', type=str, help='The city to travel to')
    parser.add_argument(
        '--interval', metavar='INTERVAL', type=int, default=60,
        help='Interval time for scan in seconds (default 60)')
    parser.add_argument(
        '--fromfile', action="store_true", help='Load trips from `wanted.txt` instead')
    parser.add_argument(
        '--fuzzy', action="store_true",
        help="Allow non-exact matches for city names, by only looking at the first word (e.g. "
             "`Trondheim LUFTHAVN VÆRNES` would match if you have entered `Trondheim`)"
    )

    args = parser.parse_args()

    if args.usr is None:
        parser.error(message="You need to provide your pushover user key.")

    if args.app is None:
        parser.error(message="You need to provide your pushover app token.")

    if args.fromfile:
        if args.from_city or args.to_city:
            print("`--fromfile` has precedence over `-from-city` and `-to-city`. Ignoring these two commands...")
        if not os.path.exists('wanted.txt'):
            parser.error(message="You need a file called `wanted.txt` in order to use the --fromfile command")
    elif args.from_city is None:
        parser.error(message="You need to provide a from value.")
    elif args.to_city is None:
        parser.error(message="You need to provide a to value.")

    return args


async def main():
    try:
        args = _set_up_arguments()
        returbil = Returbil(args=args)

        Logger.add_entry(None)
        Logger.add_entry("** Program startup **")

        while True:
            Logger.add_entry("Started looking for available trips...")
            await returbil.parse_web_page()
            await asyncio.sleep(delay=args.interval)

    except Exception as e:
        Logger.add_entry(f"ERROR: {e}")


if __name__ == "__main__":
    asyncio.run(main())
