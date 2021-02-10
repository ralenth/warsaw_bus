from .fetcher import Fetcher

import collections
import datetime
import json
import requests


class ScheduleFetcher(Fetcher):
    """Class for fetching bus schedule."""

    def fetch(self):
        """Get current schedule."""

        resource_id = 'ab75c33d-3a26-4342-b36a-6e5fef0a3ac3'
        url = f'https://api.um.warszawa.pl/api/action/dbstore_get/' \
              f'?id={resource_id}&apikey={self.api_key}'

        response = requests.get(url)
        self.process_stops(json.loads(response.text)['result'])

    def process_stops(self, stops):
        """Parse stops data."""

        current = collections.defaultdict(str)

        for stop in stops:
            stop = self.normalize(stop)
            ident = (stop['zespol'], stop['slupek'])
            # get rid of old stops locations
            current[ident] = max(current[ident], stop['obowiazuje_od'])

        for i, stop in enumerate(stops):
            stop = self.normalize(stop)
            ident = (stop['zespol'], stop['slupek'])
            if current[ident] != stop['obowiazuje_od']:
                continue

            print(f'Processing stop {i}/{len(stops)}: {stop["nazwa_zespolu"]} '
                  f'{stop["slupek"]} - {datetime.datetime.now()}')
            self.fetch_lines(stop)

    def fetch_lines(self, stop):
        """Fetch lines operating at given stop."""

        resource_id = '88cd555f-6f31-43ca-9de4-66c479ad5942'
        url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/' \
              f'?id={resource_id}&apikey={self.api_key}' \
              f'&busstopId={stop["zespol"]}&busstopNr={stop["slupek"]}'

        response = requests.get(url)
        self.process_lines(json.loads(response.text)['result'], stop)

    def process_lines(self, lines, stop):
        """Parse lines data."""

        for line in lines:
            line = self.normalize(line)
            self.fetch_schedules(line, stop)

    def fetch_schedules(self, line, stop):
        """Fetch schedule for a specific line and bus stop."""

        resource_id = 'e923fa0e-d96c-43f9-ae6e-60518c9f3238'
        url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/' \
              f'?id={resource_id}&apikey={self.api_key}' \
              f'&busstopId={stop["zespol"]}&busstopNr={stop["slupek"]}' \
              f'&line={line["linia"]}'

        response = requests.get(url)
        self.process_schedules(json.loads(response.text)['result'], line, stop)

    def process_schedules(self, schedules, line, stop):
        """Parse schedule for specific line and bus stop."""

        for schedule in schedules:
            schedule = self.normalize(schedule)
            self.data.append({
                'Lines': line['linia'],
                'Lon': stop['dlug_geo'],
                'Lat': stop['szer_geo'],
                'Brigade': schedule['brygada'],
                'BusStopName': stop['nazwa_zespolu'],
                'Time': schedule['czas']
            })

    @staticmethod
    def normalize(data):
        return {v['key']: v['value'] for v in data['values']}
