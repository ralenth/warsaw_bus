from .fetcher import Fetcher, FetcherException

import json
import requests


class PositionFetcher(Fetcher):
    """Class for fetching buses position data."""

    def __init__(self, api_key):
        super().__init__(api_key)
        self.idents = set()

    def fetch(self):
        """Get current buses positions."""

        resource_id = 'f2e5503e927d-4ad3-9500-4ab9e55deb59'
        url = f'https://api.um.warszawa.pl/api/action/busestrams_get/' \
              f'?resource_id={resource_id}&apikey={self.api_key}&type=1'

        response = requests.get(url)
        self.process_positions(json.loads(response.text)['result'])

    def process_positions(self, positions):
        """Parse positions data."""

        if not isinstance(positions, list):
            raise FetcherException('Response is not a position list')

        for position in positions:
            # delete redundant positions of specific vehicle at specific time
            ident = (position['VehicleNumber'], position['Time'])
            if ident not in self.idents:
                self.data.append(position)
                self.idents.add(ident)
