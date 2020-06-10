import requests
import re
import urllib3

from database import Database
from logger import Logger
from pushover import PushNotification

FREERIDER_SITE_ROOT = 'https://hertzfreerider.no/'
FREERIDER_REX = 'HyperLink2.+?href=\"(?P<FromStationHref>.+?)\".+?>(?P<FromStation>.+?)<.+?HyperLink3.+?href=\"(?P<ToStationHref>.+?)\".+?>(?P<ToStation>.+?)<.+?offerDate.+?>(?P<FromDate>.+?)<.+?Label1.+?>(?P<ToDate>.+?)<.+?offerDescription1.+?>(?P<Description>.+?)<'


class FreeRider:
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

        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        table_response = requests.get(url=FREERIDER_SITE_ROOT + 'unauth/list_transport_offer.aspx', verify=False)

        if table_response.status_code == 200:
            trip_entries = re.finditer(FREERIDER_REX, table_response.content.decode('utf8'), flags=re.IGNORECASE + re.MULTILINE + re.S)

            for table in trip_entries:
                trip_date = table.group('FromDate') + '-' + table.group('ToDate')
                source = table.group('FromStation')
                destination = table.group('ToStation')
                trip_id = trip_date + table.group('Description') + source + destination
                notes = table.group('Description')

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

                        booking_url = FREERIDER_SITE_ROOT + 'unauth/list_transport_offer.aspx'

                        Logger.add_entry(
                            f"Found trip on FreeRider from {source.capitalize()} to {destination.capitalize()}. "
                            f"Sending push...")

                        await push_notification.send(
                            title="🚘 Nytt treff på HertzFreeRider.no",
                            message=f"{source.capitalize()} ➡️ {destination.capitalize()}\n"
                            f"⏰ {trip_date}\n📝 {notes}",
                            url=booking_url)

                        new_trip_ids.add(trip_id)

            if new_trip_ids:
                Logger.add_entry("FreeRider can complete. Storing new trip ids in database.")
                Database.store(new_trip_ids)
            else:
                Logger.add_entry("Found no new FreeRider trips matching the provided arguments.")
