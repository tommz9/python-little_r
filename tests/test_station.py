from little_r import Station
import pytest

test_data = [
    {
        'datetime': '2016-01-01 12:01:35',
        'temperature': -14.5,
        'wind_speed': 3.16
    },
    {
        'datetime': '2016-01-01 12:02:00',
        'temperature': -14.4,
        'wind_speed': 2.5
    }
]

def test_accepts_valid_data():
    station = Station('TEST STATION', 110.5, 54.03, 450)
    records = station.generate_record(test_data)
    assert len(records) == len(test_data)



test_data_missing_datetime = [
    {
        'datetime': '2016-01-01 12:01:35',
        'temperature': -14.5,
        'wind_speed': 3.16
    },
    {
        'temperature': -14.4,
        'wind_speed': 2.5
    }
]

def test_fails_without_datetime():
    station = Station('TEST STATION', 110.5, 54.03, 450)

    with pytest.raises(KeyError):
        records = station.generate_record(test_data_missing_datetime)

def test_load_from_metadata():
    station = Station.create_from_metadata('tests/station_metadata.json')

    assert station.name == 'Test station'
