import unittest
import pandas as pd
from pandas.tseries.offsets import DateOffset

from little_rpy import time_series_to_little_r

class TimeSeriesTest(unittest.TestCase):

    def test_produces_file(self):
        station_dataframe = pd.read_csv('tests/eng-hourly-08012017-08312017.csv')
        station_dataframe.index = pd.to_datetime(station_dataframe['Date/Time']) + DateOffset(hours=7)

        selection_dataframe = station_dataframe['2017-08-26 00:00:00+00:00':'2017-08-28 00:00:00+00:00']

        time_series_to_little_r(
            selection_dataframe.index, 
            selection_dataframe['Temp (°C)'],
            'Pincher Creek',
            49.52,
            -114,
            1190,
            'temperature',
            'tests/obs')