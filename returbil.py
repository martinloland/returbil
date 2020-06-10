import requests
from bs4 import BeautifulSoup

from database import Database
from logger import Logger
from pushover import PushNotification

RETURBIL_SITE_ROOT = 'http://returbil.no/'
BG_COLORS = ('#DEE3E7', '#EFEFEF')


class Returbil:
    desired_trips = {}

    def __init__(self, args):
        self.args = args
        self.desired_trips = self._find_desired_trips()

    def _find_desired_trips(self) -> dict:
        if self.args.fromfile:
            desired_trips = {}
            with open('wanted.txt', 'r', encoding="utf8") as file:
                for trip in file:
                    source, destination = tuple(trip.strip().split(','))
                    desired_trips[source.lower()] = destination.lower()

            return desired_trips

        return {self.args.from_city.lower(): self.args.to_city.lower()}

    async def parse_web_page(self):
        push_notification = PushNotification(args=self.args)

        existing_trip_ids = Database.retrieve_all_trip_ids()
        new_trip_ids = set()

        table_response = requests.get(url=RETURBIL_SITE_ROOT + 'freecar.asp')

        if table_response.status_code == 200:
            table_soup = BeautifulSoup(table_response.content, 'html.parser')
            trip_entries = table_soup.find_all('tr', height='', bgcolor=BG_COLORS)

            for index, table in enumerate(trip_entries):
                cols = table.contents
                trip_id = str(cols[1].string)
                trip_date = str(cols[3].string)
                source = str(cols[5].string)
                destination = str(cols[7].string)

                # Sometimes, source/destination contain a choice, divided by a slash (/),
                # e.g. `Bodø Lufthavn / Trondheim Lufthavn Værnes`.
                # We parse this into a list in order to allow matching them separately.
                matching_sources = [src.strip().lower() for src in source.split('/')]
                matching_destinations = [dst.strip().lower() for dst in destination.split('/')]

                if self.args.fuzzy:
                    matching_sources = [src.split(' ')[0] for src in matching_sources]
                    matching_destinations = [dst.split(' ')[0] for dst in matching_destinations]

                if (trip_id not in existing_trip_ids
                        and all(src in self.desired_trips.keys() for src in matching_sources)
                        and any(self.desired_trips[src] in matching_destinations for src in matching_sources)):

                    trip_detail_url = RETURBIL_SITE_ROOT + table.find('a', href=True)['href']
                    detail_response = requests.get(url=trip_detail_url)

                    if detail_response.status_code == 200:
                        detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
                        trip_detail = detail_soup.find_all('tr', height='', bgcolor=BG_COLORS)[index]

                        # Check if trip is available; we don't want notifications about unbookable trips!
                        booking_detail = trip_detail.find('div', id='bookit')
                        if booking_detail:
                            notes = trip_detail.find_all('td', colspan=4)[0].string
                            booking_url = RETURBIL_SITE_ROOT + booking_detail.contents[0].attrs['href']
                            Logger.add_entry(
                                f"Found trip from {source.capitalize()} to {destination.capitalize()}. "
                                f"Sending push...")

                            await push_notification.send(
                                title="🚘 Nytt treff på Returbil.no",
                                message=f"{source.capitalize()} ➡️ {destination.capitalize()}\n"
                                f"⏰ {trip_date}\n📝 {notes}",
                                url=booking_url)

                            new_trip_ids.add(trip_id)

            if new_trip_ids:
                Logger.add_entry("Scan complete. Storing new trip ids in database.")
                Database.store(new_trip_ids)
            else:
                Logger.add_entry("Found no new trips matching the provided arguments.")
