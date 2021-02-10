import geopy.distance


class Calculator:
    """Base class for calculating statistics such as bus speed."""

    POSITION_DTYPES = {
        'Lines': str,
        'Lat': float,
        'Lon': float,
        'Time': str,
        'Brigade': str,
        'VehicleNumber': str,
    }

    SCHEDULE_DTYPES = {
        'Lines': str,
        'Lat': float,
        'Lon': float,
        'Time': str,
        'Brigade': str,
        'BusStopName': str,
    }

    def __init__(self):
        self.data = None

    @staticmethod
    def get_distance(row1, row2):
        """Get km distance of two points."""

        return geopy.distance.distance((row1['Lat'], row1['Lon']),
                                       (row2['Lat'], row2['Lon'])).km

    def save(self, filename):
        self.data.to_csv(filename)
