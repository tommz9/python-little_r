'''
Functions for converting a time series to a little_r file.
'''

from .record_formats import Record

def time_series_to_little_r(timestamps, data, station_id, lat, lon, height, variable, obs_filename, 
                            convert_to_kelvin=True):
    ''' Converts the time series (timestamps, data) of a variable to a little_r file.

    station_id, lat, lon are the weather station metadata.

    A new directory is created for each time
    obs_filename:<YYYY-MM-DD_HH>
    
    obs_filename can contain the path
    '''

    if len(timestamps) != len(data):
        raise ValueError('timestamps and data do not have the same length')


    if convert_to_kelvin and variable == 'temperature':
        data = data + 273.15


    for timestamp, data_point in zip(timestamps, data):

        date_string = timestamp.strftime("%Y-%m-%d_%H")

        filename = '{}:{}'.format(obs_filename, date_string)

        with open(filename, 'w') as f:
                record = Record(station_id, lat, lon, height, timestamp)
                record[variable] = data_point

                f.write(record.little_r_report())
