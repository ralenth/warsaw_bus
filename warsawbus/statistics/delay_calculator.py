import datetime

import dateutil.parser
import numpy as np
import pandas as pd

from .calculator import Calculator


class DelayCalculator(Calculator):
    """Class for calculating bus delays."""

    def __init__(self, schedules_filename, positions_filename, start, end):
        super().__init__()
        self.data = pd.read_csv(schedules_filename, index_col=0,
                                dtype=self.SCHEDULE_DTYPES)
        self.pos = pd.read_csv(positions_filename, index_col=0,
                               dtype=self.POSITION_DTYPES)
        self._prepare_data(start, end)

    def _prepare_data(self, start, end):
        """Parse data.

        Only data from the time period specified by start and end will be kept.
        """

        # differentiate between vehicles based on their line and brigade
        # (since there's no information about their numbers)
        self.data.sort_values(['Lines', 'Brigade'], inplace=True)

        def normalize(time):
            hour = int(time[:2])
            # night buses schedule is given as past 24:00 (i.e. 25:00 means 1 a.m.)
            time = time if hour < 24 else f'{hour - 24:02d}{time[2:]}'
            timestamp = dateutil.parser.parse(time)
            return datetime.datetime(year=start.year, month=start.month,
                                     day=start.day, hour=timestamp.hour,
                                     minute=timestamp.minute)

        # differentiate between delay 0 and non-computed one
        # (i.e. because two adjacent rows are representing different vehicles)
        self.data['Delay'] = np.nan
        self.data['Time'] = self.data['Time'].apply(normalize)
        self.data = self.data[self.data['Time'].between(start, end)]

        self.pos['Distance'] = np.nan
        self.pos['Time'] = self.pos['Time'].apply(dateutil.parser.parse)

    def calculate(self):
        """Calculate bus delays."""

        # current line and brigade of interests
        line, brigade = None, None
        # all gathered data about current line and brigade
        pos_line, pos_brigade = None, None

        for _, row in self.data.iterrows():
            # if adjacent rows are representing different line
            if row['Lines'] != line:
                line, brigade = row['Lines'], row['Brigade']
                pos_line = self.pos[self.pos['Lines'] == line].copy()
                pos_brigade = pos_line[pos_line['Brigade'] == brigade].copy()
                print(f'Line {line}')

            # if adjacent rows are representing same line, but different brigade
            elif row['Brigade'] != brigade:
                brigade = row['Brigade']
                pos_brigade = pos_line[pos_line['Brigade'] == brigade].copy()

            # consider only positions from 5 minutes before planned arrival
            # to any time past arrival
            time_threshold = row['Time'] - datetime.timedelta(minutes=5)
            # consider only buses in less than 250 m from bus stop location
            distance_threshold = 0.25

            pos_brigade['Distance'] = pos_brigade.apply(
                lambda r: self.get_distance(r, row), axis=1
            )
            pos = pos_brigade[(pos_brigade['Time'] >= time_threshold) &
                              (pos_brigade['Distance'] < distance_threshold)]

            # when got a match
            if not pos.empty:
                # choose minimum arrival time
                arrival = pos[pos['Time'] == pos['Time'].min()].iloc[0]
                # compute delay in minutes
                seconds = (arrival['Time'] - row['Time']).total_seconds()
                delay = max(seconds // 60, 0)
                self.data.loc[row.name, 'Delay'] = delay
