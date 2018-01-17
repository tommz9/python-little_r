import glob
import logging
import sys

from .station import Station

class StationSet:
    def __init__(self, folder):
        self.folder = folder

        self.stations = []
        self.reports = []

        self.logger = logging.getLogger('Station set')

    def discover_stations(self):
        
        json_files = glob.glob(self.folder + '/*.json')

        if not json_files:
            self.logger.info('Cannot find any json files in %s', self.folder)

        for json_file in json_files:

            try:
                station = Station.create_from_metadata(json_file)
            except KeyError:
                self.logger.debug('Cannot process file %s', json_file)
                continue

            self.logger.info('Found station in %s', json_file)

            self.stations.append(station)
    
    def generate_reports(self):

        self.reports = []

        for station in self.stations:
            self.reports.append(station.generate_record_from_data_file(
                lambda x: x.format('YYYY-MM-DD_HH')))

    def generate_files(self, output_directory, prefix):
        
        intervals = self.reports[0].keys()

        for interval in intervals:
            fn = output_directory + '/obs:' + interval
            with open(fn, "w") as output_file:
                for report in self.reports:
                    try:
                        output_file.writelines(report[interval])
                    except KeyError:
                        pass


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)

    if len(sys.argv) != 2:
        logging.error('Folder missing')
        sys.exit(1)

    folder = sys.argv[1]

    station_set = StationSet(folder)

    station_set.discover_stations()
    station_set.generate_reports()

    station_set.generate_files(folder, 'obs')

