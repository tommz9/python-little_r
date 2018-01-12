import unittest
from datetime import datetime

from little_r.record_formats import Record

class TestRecord(unittest.TestCase):

    def create_sample_record(self, **kwargs):
        '''
        Creates a toy record.abs
        '''
        return Record('TestName', 100, 50, None, datetime(2017, 1, 1, 18, 30, 0), **kwargs)

    def test_getitem(self):
        r = self.create_sample_record(temperature=100.0)

        self.assertEqual(r['temperature'], 100.0)

    def test_setitem(self):
        r = Record('TestName', 100, 50, None, '2017-01-01')

        r['temperature'] = 100.0
        self.assertEqual(r['temperature'], 100.0)

    def test_setitem_ignores_unknown(self):

        r = self.create_sample_record()

        with self.assertRaises(KeyError):
            r['something'] = 100.0

    def test_date_format(self):
        
        r = self.create_sample_record()

        self.assertEqual(r.get_formated_time(), '20170101183000')

    def test_end_of_record(self):

        r = self.create_sample_record()

        self.assertEqual(r.end_of_message_line(), '      1      0      0')

    def test_data_field_all_empty(self):

        r = self.create_sample_record()

        expected_output = '-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'

        self.assertEqual(r.data_record(), expected_output)

    def test_data_field_one_set(self):

        r = self.create_sample_record()

        r['temperature'] = 453.14999

        expected_output = '-888888.00000      0-888888.00000      0    453.14999      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'

        self.assertEqual(r.data_record(), expected_output)

    def test_closing_line(self):
        r = self.create_sample_record()

        expected_output = '-777777.00000      0-777777.00000      0      1.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'

        self.assertEqual(r.data_closing_line(), expected_output)


    def test_generate_header(self):

        self.maxDiff = None

        r = Record('Chieti 14.181 42.377 ', 42.377, 14.181, None, datetime(2011, 10, 25, 6, 30, 0))

        # expected_output = '            42.37700            14.18100Chieti 14.181 42.377 xxxxxxxxxxxxxxxxxxxSURFACE DATA FROM MY DATABASExxxxxxxxxxxFM-12 SYNOPxxxxxxxxxxxxxxxxxxxxxxxxxxxxxI did itxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx       -888888.00000         6         0         0         0         0         F         F         F   -888888   -888888      20111025063000-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0-888888.00000      0'

        # Just check the lenght
        self.assertEqual(len(r.message_header()), 600)

if __name__ == '__main__':
    unittest.main()
