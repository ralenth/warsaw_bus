from .calculator import Calculator

import dateutil.parser

import numpy as np
import pandas as pd


class SpeedCalculator(Calculator):
    """Class for calculating bus speed statistics."""

    def __init__(self, positions_filename, start, end):
        super().__init__()
        self.data = pd.read_csv(positions_filename, index_col=0,
                                dtype=self.POSITION_DTYPES)
        self._prepare_data(start, end)

    def _prepare_data(self, start, end):
        """Parse data.

        Only data from the time period specified by start and end will be kept.
        """

        self.data.sort_values(['VehicleNumber', 'Time'], inplace=True)

        # differentiate between distance 0 and non-computed one
        self.data['Distance'] = np.nan
        self.data['Speed'] = np.nan
        self.data['Time'] = self.data['Time'].apply(dateutil.parser.parse)
        self.data = self.data[self.data['Time'].between(start, end)]

    def calculate(self):
        """Calculate speed."""

        for i in range(len(self.data) - 1):
            row1, row2 = self.data.iloc[i], self.data.iloc[i + 1]

            # skip different vehicles
            if row1['VehicleNumber'] != row2['VehicleNumber']:
                continue

            distance = self.get_distance(row1, row2)
            self.data.loc[row2.name, 'Distance'] = distance

            time_delta = row2['Time'] - row1['Time']
            # seconds to hours, so speed would be in km/h
            time_delta = time_delta.total_seconds() / 3600
            self.data.loc[row2.name, 'Speed'] = distance / time_delta
