import pandas as pd
import plotly.graph_objects as go


class WarsawPlotter:
    """Class for visualizing geo data on Warsaw map."""

    # center coordinates of the city
    COORDS = (52.235176, 21.008393)
    # initial map zoom
    ZOOM = 10
    MAP_STYLE = 'carto-positron'
    POSSIBLE_DTYPES = {
        'Lines': str,
        'Lat': float,
        'Lon': float,
        'Time': str,
        'Brigade': str,
        'Distance': float,
        'VehicleNumber': str,
        'Delay': float,
        'Speed': float,
    }

    def __init__(self, filename, column_name, bounds):
        """Initialize WarsawPlotter.

        Parameters
        ----------
        filename : str
            Path to a .csv filename containing computed statistics.
        column_name : str
            Name of column of interest, so column, which values will be plotted on map.
        bounds : tuple
            Minimum and maximum value for column of interest, resulting in a clear, human-readable plot.
        """

        self.data = pd.read_csv(filename, index_col=0, dtype=self.POSSIBLE_DTYPES)
        self.column_name = column_name

        self._prepare_data(bounds)

    def _prepare_data(self, bounds):
        """Parse data."""

        # remove rows with incomplete information
        self.data.dropna(inplace=True)
        self.data = self.data[self.data[self.column_name].between(*bounds)]
        # remove coordinate duplicates
        self.data = self.data.groupby(['Lat', 'Lon']).mean().reset_index()

    def plot(self, filename, title, size, opacity, colorscale):
        """Create plot.

        Parameters
        ----------
        filename : str
            Plot destination filename. If empty, no file will be created.
        title : str
        size : float
            Size of markers of each point.
        opacity : float
            Opacity of markers of each point.
        colorscale : str
        """

        scatter_map = self._prepare_map(size, opacity, colorscale)
        layout = self._prepare_layout(title)

        figure = go.Figure(data=[scatter_map], layout=layout)
        self._save(filename, figure)

        figure.show()

    def _save(self, filename, figure):
        """Save plot to .html or static file."""

        html_endings = ['html']
        image_endings = ['png', 'jpeg', 'jpg']

        if not filename:
            return

        for ending in html_endings:
            if filename.endswith(ending):
                figure.write_html(filename)
                return

        for ending in image_endings:
            if filename.endswith(ending):
                figure.write_image(filename, engine='kaleido')
                return

    def _prepare_map(self, size, opacity, colorscale):
        """Create a map skeleton.

        Parameters
        ----------
        size : float
            Size of markers of each point.
        opacity : float
            Opacity of markers of each point.
        colorscale : str
        """

        args = {
            'lat': self.data['Lat'],
            'lon': self.data['Lon'],
            'text': self.data[self.column_name],
            'mode': 'markers',
            'marker': {
                'size': size,
                'opacity': opacity,
                'color': self.data[self.column_name],
                'colorscale': colorscale,
                'cauto': True,
                'showscale': True,
            }
        }

        return go.Scattermapbox(**args)

    def _prepare_layout(self, title):
        """Create plot layout.

         Parameters
         ----------
         title : str
         """

        args = {
            'title': title,
            'title_x': 0.5,
            'height': 800,
            'margin': {
                't': 80,
                'b': 10,
                'l': 0,
                'r': 10,
            },
            'font': {
                'color': 'darkgreen',
                'size': 18,
            },
            'mapbox': {
                'center': {
                    'lat': self.COORDS[0],
                    'lon': self.COORDS[1],
                },
                'zoom': self.ZOOM,
                'style': self.MAP_STYLE,
            }
        }

        return go.Layout(**args)
