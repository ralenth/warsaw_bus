import copy
import dateutil.parser

import numpy as np
import pandas as pd

from .calculator import Calculator
from .delay_calculator import DelayCalculator
from .speed_calculator import SpeedCalculator


class TestBaseCalculator:
    def test_distance(self):
        calculator = Calculator()

        assert calculator.get_distance({'Lat': 20, 'Lon': 20},
                                       {'Lat': 20, 'Lon': 20}) == 0
        assert calculator.get_distance({'Lat': 20, 'Lon': 20},
                                       {'Lat': 21, 'Lon': 21}) > 0


class TestSpeedCalculator:
    def test_calculate(self, tmpdir):
        positions = []
        for line in range(100, 110):
            for i in range(60):
                positions.append({
                    'Lines': str(line),
                    'Lat': 0 if i % 2 else 0.01,
                    'Lon': 0 if i % 2 else 0.01,
                    'VehicleNumber': str(line),
                    'Time': dateutil.parser.parse(f'2021-02-02 16:{i:02d}:00'),
                    'Brigade': '0',
                })

        pd.DataFrame(positions).to_csv(tmpdir / 'positions.csv')

        expected_data = pd.DataFrame(positions)
        expected_data['Distance'] = expected_data.apply(
            lambda r: 0 if r['Time'].minute == 0 else 1.5690347154047222,
            axis=1
        )
        expected_data['Speed'] = expected_data.apply(
            lambda r: 0 if r['Time'].minute == 0 else 94.14208292428333,
            axis=1
        )

        calculator = SpeedCalculator(
            positions_filename=tmpdir / 'positions.csv',
            start=dateutil.parser.parse('2021-02-02 16:00:00'),
            end=dateutil.parser.parse('2021-02-02 17:00:00'),
        )

        calculator.calculate()

        assert (calculator.data.fillna(0) == expected_data).all(axis=None)


class TestDelayCalculator:
    def test_calculate(self, tmpdir):
        schedules = []
        positions = []

        for line in range(100, 110):
            for i in range(10):
                schedules.append({
                    'Lines': str(line),
                    'Lat': 0,
                    'Lon': 0,
                    'Brigade': str(i),
                    'BusStopName': 'Banacha',
                    'Time': dateutil.parser.parse('2021-02-02 16:00:00')
                })

                positions.append({
                    'Lines': str(line),
                    'Lat': 0,
                    'Lon': 0,
                    'VehicleNumber': f'{line}_{i}',
                    'Time': dateutil.parser.parse(f'2021-02-02 16:{i:02d}:00'),
                    'Brigade': str(i),
                })

        pd.DataFrame(schedules).to_csv(tmpdir / 'schedules.csv')
        pd.DataFrame(positions).to_csv(tmpdir / 'positions.csv')

        expected_data = pd.DataFrame(schedules)
        expected_data['Delay'] = expected_data['Brigade'].apply(int)

        calculator = DelayCalculator(
            schedules_filename=tmpdir / 'schedules.csv',
            positions_filename=tmpdir / 'positions.csv',
            start=dateutil.parser.parse('2021-02-02 16:00:00'),
            end=dateutil.parser.parse('2021-02-02 17:00:00'),
        )

        calculator.calculate()

        assert (calculator.data.fillna(0) == expected_data).all(axis=None)
