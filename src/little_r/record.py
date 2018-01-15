from collections import namedtuple
from datetime import datetime
import fortranformat as ff

'''

Take from: csv2little_r.f
Author: Valerio Capecchi <capecchi@lamma.rete.toscana.it>

Github: https://github.com/valcap/csv2little_r


c     ... this is a little testing routine that is supposed to generate a 
c         single sounding that the objective analysis program will ingest

c     ... pressure is in Pa, height in m, temperature and dew point are in
c         K, speed is in m/s, and direction is in degrees

c     ... sea level pressure is in Pa, terrain elevation is in m, latitude
c         is in degrees N, longitude is in degrees E

c     ... to put in a surface observation, make only a single level "sounding"
c         and make the value of the height equal the terrain elevation -- PRESTO!

c     ... the first 40 character string may be used for the description of
c         the station (i.e. name city country, etc)

c     ... the second character string we use for our source

c     ... the third string should be left alone, it uses the phrase "FM-35 TEMP"
c         for an upper air station, and should use "FM-12 SYNOP" for surface data

c     ... the fourth string is unused, feel free to experiment with labels!

c     ... bogus data are not subject to quality control

c     ... There are 3 records for each observation site:
c     1. a header that contains information about station identifier, 
c        station location, data information, station elevation
c        and whether the report is a bogus or not, etc;
c     2. a report (whether it is a sounding containing many levels, or only a surface report)
c     3. an end-of-message line.

c     ... For a surface observation, the geopotential height (z(k)) 
c         must be set equal to the terrain elevation (ter) field.
c         This is the definition of a surface observation. 




c    ... Define writing formats

c    ini_format writes an header:
ccc    two integers --> 2f20.5
ccc                    station latitude (north positive)
ccc                    station longitude (east positive)
ccc    string1, string2, string3, string4 --> 2a40 & 2a40
ccc                    string1 ID of station
ccc                    string2 Name of station
ccc                    string3 Description of the measurement device
ccc                    string4 GTS, NCAR/ADP, BOGUS, etc.
ccc    terrain elevation (m) --> 1f20.5
ccc    five integers: kx*6, 0, 0, iseq_num, 0 --> 5i10
ccc                    Number of valid fields in the report
ccc                    Number of errors encountered during the decoding of this observation
ccc                    Number of warnings encountered during decoding of this observation
ccc                    Sequence number of this observation
ccc                    Number of duplicates found for this observation
ccc    three logicals: is_sounding, bogus, .false. --> 3L10
ccc                    Multiple levels or a single level
ccc                    bogus report or normal one
ccc                    Duplicate and discarded (or merged) report
ccc    two integers --> 2i10
ccc                    Seconds since 0000 UTC 1 January 1970
ccc                    Day of the year
ccc    date of observation as character --> a20
ccc                    YYYYMMDDHHmmss
ccc    13 couples of numbers --> 13(f13.5,i7)
ccc                    1. Sea-level pressure (Pa) and a QC flag
ccc                    2. Reference pressure level (for thickness) (Pa) and a QC flag
ccc                    3. Ground Temperature (T) and QC flag
ccc                    4. Sea-Surface Temperature (K) and QC
ccc                    5. Surface pressure (Pa) and QC
ccc                    6. Precipitation Accumulation and QC
ccc                    7. Daily maximum T (K) and QC
ccc                    8. Daily minimum T (K) and QC
ccc                    9. Overnight minimum T (K) and QC
ccc                    10. 3-hour pressure change (Pa) and QC
ccc                    11. 24-hour pressure change (Pa) and QC
ccc                    12. Total cloud cover (oktas) and QC
ccc                    13. Height (m) of cloud base and QC
      ini_format =  ' ( 2f20.5 , 2a40 , 2a40 , 1f20.5 , 5i10 , 3L10 , 2i10 , a20 ,  13( f13.5 , i7 ) ) '

c    mid_format writes the actual observations:
ccc    ten floating numbers and integers --> 10( f13.5 , i7 )
ccc       1. Pressure (Pa) of observation, and QC
ccc       2. Height (m MSL) of observation, and QC
ccc       3. Temperature (K) and QC
ccc       4. Dewpoint (K) and QC
ccc       5. Wind speed (m s-1 ) and QC
ccc       6. Wind direction (degrees) and QC
ccc       7. U component of wind (m s-1 ), and QC
ccc       8. V component of wind (m s-1 ), and QC
ccc       9. Relative Humidity (%) and QC
ccc      10. Thickness (m), and QC
      mid_format =  ' ( 10( f13.5 , i7 ) ) '

c    end_format writes the tail of the little_r file
ccc    three integers --> 3 ( i7 )
ccc      Number of valid fields in the report
ccc      Number of errors encountered during the decoding of the report
ccc      Number of warnings encountered during the decoding the report
      end_format = ' ( 3 ( i7 ) ) ' 
c    ... End of writing formats
'''

HEADER_FORMAT = '( 2f20.5 , 2a40 , 2a40 , 1f20.5 , 5i10 , 3L10 , 2i10 , a20 ,  13( f13.5 , i7 ) )'

DATA_FORMAT = '( 10( f13.5 , i7 ) )'

END_FORMAT = '( 3 ( i7 ) )'

UNDEFINED_VALUE = -888888

header_writer = ff.FortranRecordWriter(HEADER_FORMAT)
data_writer = ff.FortranRecordWriter(DATA_FORMAT)
end_writer = ff.FortranRecordWriter(END_FORMAT)


def replace_undefined(data):
    return [UNDEFINED_VALUE if x is None else x for x in data]

class Record:
    '''
    Represents one record in the observation file

    The record is identified by name, lat, lon and time and can have several optional measurements.

    Multiple measurements allow to enter measurements in several heights.

    Currently, only one measurement per record is supported
    '''

    def __init__(self, station_name, lat, lon, height, time, **kwargs):
        self.station_name = station_name
        self.lat = lat
        self.lon = lon
        self.time = time
        self.height = height

        self.measurements = {
            'temperature': None,
            'dewpoint': None,
            'wind_speed': None,
            'wind_direction': None,
            'wind_u': None,
            'wind_v': None,
            'humidity': None,
            'thickness': None
        }

        self.merge(kwargs)

    def merge(self, merge_with):
        ''' Updates the record with new measurements
        '''
        if not self.measurements.keys() >= merge_with.keys():
            raise ValueError(
                'Unknown measurement name {}'.format(merge_with.keys() - self.measurements.keys()))

        self.measurements.update(merge_with)

    def __getitem__(self, key):
        return self.measurements[key]

    def __setitem__(self, key, value):
        if key not in self.measurements:
            raise KeyError('Unknown measurement name {}'.format(key))

        self.measurements[key] = value

    def get_formated_time(self):
        ''' Returns properly formated time.
        Little_r format is YYYYMMDDHHmmss
        '''

        return self.time.strftime('%Y%m%d%H%M%S')

    def end_of_message_line(self):
        ''' This line has to be at the end of the report after the data closing line
        '''

        return end_writer.write([1, 0, 0])

    def data_record(self):
        ''' Generates one line of the data section in the little_r format.
        Only one point of data is supported.
        '''

        data = [
            None, 0,    # Pressure (Pa) of observation, and QC
            self.height, 0,    # Height (m MSL) of observation, and QC
            self.measurements['temperature'], 0,    # Temperature (K) and QC
            self.measurements['dewpoint'], 0,    # Dewpoint (K) and QC
            self.measurements['wind_speed'], 0,    # Wind speed (m s-1 ) and QC
            self.measurements['wind_direction'], 0,    # Wind direction (degrees) and QC
            self.measurements['wind_u'], 0,    # U component of wind (m s-1 ), and QC
            self.measurements['wind_v'], 0,    # V component of wind (m s-1 ), and QC
            self.measurements['humidity'], 0,    # Relative Humidity (%) and QC
            self.measurements['thickness'], 0,    # Thickness (m), and QC
        ]

        data = replace_undefined(data)
        return data_writer.write(data)

    def data_closing_line(self):
        ''' Generates a line that has to be at the end of the data block
        '''
        data = [
            -777777, 0,    # Pressure (Pa) of observation, and QC
            -777777, 0,    # Height (m MSL) of observation, and QC
            1.0, 0,    # should be the number of data record? (Temperature (K) and QC)
            None, 0,    # Dewpoint (K) and QC
            None, 0,    # Wind speed (m s-1 ) and QC
            None, 0,    # Wind direction (degrees) and QC
            None, 0,    # U component of wind (m s-1 ), and QC
            None, 0,    # V component of wind (m s-1 ), and QC
            None, 0,    # Relative Humidity (%) and QC
            None, 0,    # Thickness (m), and QC
        ]

        data = replace_undefined(data)
        return data_writer.write(data)

    def message_header(self):
        ''' Generates the header in little_r format
        '''

        data = [
            self.lat,  #                   station latitude (north positive)
            self.lon,  #                   station longitude (east positive)
            self.station_name,  #                   string1 ID of station
            'Station name',  #                   string2 Name of station
            'FM-12 SYNOP',  #                   string3 Description of the measurement device
            'String 4',  #                   string4 GTS, NCAR/ADP, BOGUS, etc.
            self.height,  #                   terrain elevation (m) --> 1f20.5
            6,     #                   Number of valid fields in the report (kx*6)
            0,     #                   Number of errors encountered during the decoding of this observation (0)
            0,     #                   Number of warnings encountered during decoding of this observation (0)
            1,     #                   Sequence number of this observation (iseq_num)
            0,     #                   Number of duplicates found for this observation (0)
            False,  #                   Multiple levels or a single level (is_sounding)
            False,  #                   bogus report or normal one
            False,  #                   Duplicate and discarded (or merged) report
            None,  #                   Seconds since 0000 UTC 1 January 1970
            None,  #                   Day of the year
            self.get_formated_time(),  #                   date of observation as character --> a20
            None,  #                   1. Sea-level pressure (Pa) and a QC flag
            0,
            None,  #                   2. Reference pressure level (for thickness) (Pa) and a QC flag
            0,
            None,  #                   3. Ground Temperature (T) and QC flag
            0,
            None,  #                   4. Sea-Surface Temperature (K) and QC
            0,
            None,  #                   5. Surface pressure (Pa) and QC
            0,
            None,  #                   6. Precipitation Accumulation and QC
            0,
            None,  #                   7. Daily maximum T (K) and QC
            0,
            None,  #                   8. Daily minimum T (K) and QC
            0,
            None,  #                   9. Overnight minimum T (K) and QC
            0,
            None,  #                   10. 3-hour pressure change (Pa) and QC
            0,
            None,  #                   11. 24-hour pressure change (Pa) and QC
            0,
            None,  #                   12. Total cloud cover (oktas) and QC
            0,
            None,   #                   13. Height (m) of cloud base and QC
            0
        ]

        data = replace_undefined(data)
        return header_writer.write(data)

    def little_r_report(self):
        ''' Generates a report in the little_r format
        '''

        output = [
            self.message_header(),
            self.data_record(),
            self.data_closing_line(),
            self.end_of_message_line()]

        return '\n'.join(output) + '\n'
