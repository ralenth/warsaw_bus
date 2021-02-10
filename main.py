import argparse
import datetime
import dateutil.parser

import warsawbus


API_KEY = 'cffe0ff6-e7ac-4bfe-8790-c2922c069248'


def initialize_parser():
    parser = argparse.ArgumentParser(description='Warsaw Bus analytics tool.')
    subparsers = parser.add_subparsers(dest='subcommand',
                                       help='Choose analytics command.')

    # Add positions sub parser
    _parser = subparsers.add_parser('positions', help='Fetch bus positions')
    _parser.add_argument('--api_key', type=str, help='API key')
    _parser.add_argument('--file', type=str, help='Data destination filename')
    _parser.add_argument('--start', type=str, help='Fetching start timestamp')
    _parser.add_argument('--end', type=str, help='Fetching end timestamp')

    # Add schedules sub parser
    _parser = subparsers.add_parser('schedules', help='Fetch bus schedules')
    _parser.add_argument('--api_key', type=str, help='API key')
    _parser.add_argument('--file', type=str, help='Data destination filename')

    # Add speed sub parser
    _parser = subparsers.add_parser('speeds', help='Calculate bus speeds')
    _parser.add_argument('--file', type=str, help='Data destination filename')
    _parser.add_argument('--positions', type=str, help='Positions filename')
    _parser.add_argument('--start', type=str, help='Fetching start timestamp')
    _parser.add_argument('--end', type=str, help='Fetching end timestamp')
    _parser.add_argument('--dry', dest='dry', action='store_true',
                         help='Dry run - just visualise data')

    # Add delay sub parser
    _parser = subparsers.add_parser('delays', help='Calculate bus delays')
    _parser.add_argument('--file', type=str, help='Data destination filename')
    _parser.add_argument('--schedules', type=str, help='Schedules filename')
    _parser.add_argument('--positions', type=str, help='Positions filename')
    _parser.add_argument('--start', type=str, help='Fetching start timestamp')
    _parser.add_argument('--end', type=str, help='Fetching end timestamp')
    _parser.add_argument('--dry', dest='dry', action='store_true',
                         help='Dry run - just visualise data')

    return parser


def fetch_positions(args):
    fetcher = warsawbus.PositionFetcher(api_key=args.api_key)
    fetcher.fetch_loop(
        start=dateutil.parser.parse(args.start),
        end=dateutil.parser.parse(args.end),
        step=datetime.timedelta(seconds=15)
    )
    fetcher.save(filename=args.file)


def fetch_schedules(args):
    fetcher = warsawbus.ScheduleFetcher(api_key=args.api_key)
    fetcher.fetch()
    fetcher.save(filename=args.file)


def calculate_speeds(args):
    if not args.dry:
        calculator = warsawbus.SpeedCalculator(
            positions_filename=args.positions,
            start=dateutil.parser.parse(args.start),
            end=dateutil.parser.parse(args.end),
        )
        calculator.calculate()
        calculator.save(filename=args.file)

    plotter = warsawbus.WarsawPlotter(filename=args.file, column_name='Speed',
                                      bounds=(30, 100))
    plotter.plot(filename='', title='Warsaw buses speed [km/h]',
                 size=5, opacity=0.9, colorscale='speed')


def calculate_delays(args):
    if not args.dry:
        calculator = warsawbus.DelayCalculator(
            schedules_filename=args.schedules,
            positions_filename=args.positions,
            start=dateutil.parser.parse(args.start),
            end=dateutil.parser.parse(args.end),
        )
        calculator.calculate()
        calculator.save(filename=args.file)

    plotter = warsawbus.WarsawPlotter(filename=args.file, column_name='Delay',
                                      bounds=(0, 20))
    plotter.plot(filename='', title='Warsaw buses delays [min]',
                 size=10, opacity=0.9, colorscale='Burgyl')


if __name__ == '__main__':
    parser = initialize_parser()
    args = parser.parse_args()

    if args.subcommand == 'positions':
        fetch_positions(args)
    elif args.subcommand == 'schedules':
        fetch_schedules(args)
    elif args.subcommand == 'speeds':
        calculate_speeds(args)
    elif args.subcommand == 'delays':
        calculate_delays(args)
