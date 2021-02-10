import pandas as pd
import pytest
import unittest.mock

from .fetcher import (
    Fetcher,
    FetcherException,
)
from .position_fetcher import PositionFetcher
from .schedule_fetcher import ScheduleFetcher


class TestBaseFetcher:
    def test_non_implemented_fetch(self):
        fetcher = Fetcher(api_key='foo')

        with pytest.raises(NotImplementedError):
            fetcher.fetch()

    def test_save(self, tmpdir):
        example_data = [
            {'a': 1, 'b': 2},
            {'a': 3, 'b': 4},
        ]

        fetcher = Fetcher(api_key='foo')
        fetcher.data = example_data
        fetcher.save(tmpdir / 'file.csv')

        example_df = pd.DataFrame(example_data)
        saved_df = pd.read_csv(tmpdir / 'file.csv', index_col=0)
        assert (example_df == saved_df).all(axis=None)


class TestPositionFetcher:
    @unittest.mock.patch.object(PositionFetcher, 'process_positions')
    def test_fetch(self, mock, requests_mock):
        url = f'https://api.um.warszawa.pl/api/action/busestrams_get/' \
              f'?resource_id=f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=foo' \
              f'&type=1'
        requests_mock.get(url, text='{"result": "bar"}')

        fetcher = PositionFetcher(api_key='foo')
        fetcher.fetch()
        mock.assert_called_with('bar')

    def test_process_positions_exception(self):
        fetcher = PositionFetcher(api_key='foo')

        with pytest.raises(FetcherException):
            fetcher.process_positions('bar')

    def test_process_positions_unique(self):
        positions = [{
            'Lines': '523',
            'Lon': 20 + i,
            'Lat': 50 + i,
            'VehicleNumber': i,
            'Time': f'2021-02-02 17:{i:02d}:27',
        } for i in range(10)]

        fetcher = PositionFetcher(api_key='foo')
        fetcher.process_positions(positions)
        assert fetcher.data == positions

    def test_process_positions_repeating(self):
        positions = [{
            'Lines': '523',
            'Lon': 20 + i,
            'Lat': 50 + i,
            'VehicleNumber': 0,
            'Time': '2021-02-02 17:00:27',
        } for i in range(10)]

        fetcher = PositionFetcher(api_key='foo')
        fetcher.process_positions(positions)
        assert fetcher.data == [positions[0]]


class TestScheduleFetcher:
    STOPS = [{
        'dlug_geo': 20,
        'szer_geo': 50,
        'nazwa_zespolu': 'Banacha',
        'obowiazuje_od': '2020-01-01 00:00:00',
        'zespol': 420,
        'slupek': str(i)
    } for i in range(10)]

    LINES = [{
        'linia': str(i)
    } for i in range(100, 110)]

    SCHEDULES = [{
        'brygada': str(i),
        'czas': '2021-02-02 17:00:27'
    } for i in range(10)]

    @unittest.mock.patch.object(ScheduleFetcher, 'process_stops')
    def test_fetch(self, mock, requests_mock):
        url = f'https://api.um.warszawa.pl/api/action/dbstore_get/' \
              f'?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey=foo'
        requests_mock.get(url, text='{"result": "bar"}')

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.fetch()

        mock.assert_called_with('bar')

    @unittest.mock.patch.object(ScheduleFetcher, 'fetch_lines')
    def test_process_stops(self, mock):
        expected_calls = [
            unittest.mock.call(stop) for stop in self.STOPS
        ]

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.process_stops(
            stops=[self.denormalize(data) for data in self.STOPS]
        )

        mock.assert_has_calls(expected_calls)
        assert mock.call_count == len(expected_calls)

    @unittest.mock.patch.object(ScheduleFetcher, 'process_lines')
    def test_fetch_lines(self, mock, requests_mock):
        url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/' \
              f'?id=88cd555f-6f31-43ca-9de4-66c479ad5942&apikey=foo' \
              f'&busstopId=420&busstopNr=0'
        requests_mock.get(url, text='{"result": "bar"}')

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.fetch_lines(self.STOPS[0])

        mock.assert_called_with('bar', self.STOPS[0])

    @unittest.mock.patch.object(ScheduleFetcher, 'fetch_schedules')
    def test_process_lines(self, mock):
        expected_calls = [
            unittest.mock.call(line, self.STOPS[0]) for line in self.LINES
        ]

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.process_lines(
            lines=[self.denormalize(data) for data in self.LINES],
            stop=self.STOPS[0]
        )

        mock.assert_has_calls(expected_calls)
        assert mock.call_count == len(expected_calls)

    @unittest.mock.patch.object(ScheduleFetcher, 'process_schedules')
    def test_fetch_schedules(self, mock, requests_mock):
        url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/' \
              f'?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&apikey=foo' \
              f'&busstopId=420&busstopNr=0&line=100'
        requests_mock.get(url, text='{"result": "bar"}')

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.fetch_schedules(self.LINES[0], self.STOPS[0])

        mock.assert_called_with('bar', self.LINES[0], self.STOPS[0])

    def test_process_schedules(self):
        expected_data = [{
            'Lines': '100',
            'Lon': 20,
            'Lat': 50,
            'Brigade': str(i),
            'BusStopName': 'Banacha',
            'Time': '2021-02-02 17:00:27',
        } for i in range(10)]

        fetcher = ScheduleFetcher(api_key='foo')
        fetcher.process_schedules(
            schedules=[self.denormalize(data) for data in self.SCHEDULES],
            line=self.LINES[0],
            stop=self.STOPS[0]
        )
        assert fetcher.data == expected_data

    @staticmethod
    def denormalize(data):
        return {'values': [{'key': k, 'value': v} for k, v in data.items()]}
