"""station.py

Author: Tomas Barton, tommz9@gmail.com

"""
import json
import csv
import os

import arrow

from .record import Record


class Station:
    """A factory method to create records for one station.

    Holds the information about the station name, location and height.
    """

    def __init__(self, name, lat, lon, height, data_file=None, timezone=None):
        """Create the station object."""

        self.name = name
        self.lat = lat
        self.lon = lon
        self.height = height
        self.data_file = data_file
        self.timezone = timezone

    def generate_record(self, data_dictionaries, group_by):
        """Convert the measurements to records.

        data_dictionaries is a list of dictionaries where each dictionary holds
        measurements taken in one time.

        group_by is a function that takes the time of the measurement and
        converts it to a string representing the time part of the filename for 
        the little_r file. This function can return the same value for several
        measurements (typically measurements within one hour). These
        measurement will be saved under one key in the returned dict.

        The function returns a dictionary of lists with measurements. The key
        of the dictionary is the value returned by the group_by function.
        """
        result = {}

        for one_measurement in data_dictionaries:
            time = one_measurement['datetime']

            if isinstance(time, str):
                if self.timezone:
                    time = arrow.get(time).shift(hours=6) # TODO: fix utc conversion
                else:
                    time = arrow.get(time)

            record = Record(self.name, self.lat, self.lon, self.height, time)

            del one_measurement['datetime']

            one_measurement = {k: float(v) for k, v in one_measurement.items()}

            record.merge(one_measurement)

            key = group_by(time)
            
            if key == '2016-04-01_00':
                break

            record_string = record.little_r_report()

            try:
                result[key].append(record_string)
            except KeyError:
                result[key] = [record_string]

        return result

    def generate_record_from_data_file(self, group_by, data_file_argument=None):

        if data_file_argument:
            self.data_file = data_file_argument
        
        with open(self.data_file) as f:
            reader = csv.DictReader(f)
            dictionaries = list(reader)

        return self.generate_record(dictionaries, group_by)

    @staticmethod
    def create_from_metadata(filename):
        """Create a station object based on the configuration in json file."""
        with open(filename, 'r') as f:
            metadata = json.load(f)
        
        station = Station(
            metadata['name'],
            metadata['lat'],
            metadata['lon'],
            metadata['height'],
            data_file=os.path.dirname(filename) + '/' + metadata.get('data_file'),
            timezone=metadata.get('timezone'))

        return station
