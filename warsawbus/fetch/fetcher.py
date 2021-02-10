import datetime
import time

import pandas as pd


class FetcherException(Exception):
    pass


class Fetcher:
    """Base class for fetching data."""

    def __init__(self, api_key):
        self.api_key = api_key
        self.data = []

    def fetch(self):
        raise NotImplementedError

    def fetch_loop(self, start, end, step):
        """Fetch data in a loop for a given period of time.

        Parameters
        ----------
        start : date
        end : date
        step : timedelta
        """

        next_step = start
        while datetime.datetime.now() < end:
            # wait till next_step
            while datetime.datetime.now() < next_step:
                time.sleep(5)

            print(f'Fetching at {next_step}')
            try:
                self.fetch()
                next_step = next_step + step
            except FetcherException as err:
                print(f'FetcherException ({err}) occurred, retrying request')

    def save(self, filename):
        dataframe = pd.DataFrame(self.data)
        dataframe.to_csv(filename)
