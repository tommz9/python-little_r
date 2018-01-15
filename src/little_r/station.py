from .record import Record
import arrow
import json

class Station:
    """A factory method to create records for one station.

    Holds the information about the station name, location and height.
    """

    def __init__(self, name, lat, lon, height, timezone=None):

        self.name = name
        self.lat = lat
        self.lon = lon
        self.height =  height
        self.timezone = timezone
        
    def generate_record(self, data_dictionaries):

        result = {}

        for one_measurement in data_dictionaries:
            time = one_measurement['datetime']

            if isinstance(time, str):
                if self.timezone:
                    time = arrow.get(time, self.timezone)
                else:
                    time = arrow.get(time)

            record = Record(self.name, self.lat, self.lon, self.height, time)

            del one_measurement['datetime']

            record.merge(one_measurement)

            result[time] = record.little_r_report()
        
        return result

    @staticmethod
    def create_from_metadata(filename):
        
        with open(filename, 'r') as f:
            metadata = json.load(f)
        
        station = Station(
            metadata['name'], 
            metadata['lat'], 
            metadata['lon'], 
            metadata['height'],
            timezone=metadata.get('timezone'))
    
        return station
