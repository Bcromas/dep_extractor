import unittest
import random
from extract_report_values import *

class Test_load_report(unittest.TestCase):
    """
    Test load_report() functionality for a "good" csv and a number of problematic scenarios 
    including missing, misspelled, and empty columns.
    """

    def test_good_csv(self):
        csv = "test_csvs/test.csv"
        x = load_report(csv)
        x_rand_item = random.choice(list(x.items())) # this is a tuple
        x_rand_key = x_rand_item[0]
        x_rand_vals = x_rand_item[1]

        self.assertIsInstance(x, dict) # returns a dict
        self.assertGreater(len(x.keys()), 0) # dict isn't empty
        self.assertIsInstance(x_rand_key, int)
        self.assertIsInstance(x_rand_vals, dict)
        self.assertIn("Sample Point Description".lower(),x_rand_vals.keys())
        self.assertIn("DMR Parameter Description Abbrv.".lower(),x_rand_vals.keys())
        self.assertIn("Concentrated Average Stat Base".lower(),x_rand_vals.keys())
        self.assertIn("Concentration Maximum Stat Base".lower(),x_rand_vals.keys())
        self.assertIn("Mon. Period Start Date".lower(),x_rand_vals.keys())
        self.assertIn("Reported Value Concentration Avg".lower(),x_rand_vals.keys())
        self.assertIn("Reported Value Concentration Max".lower(),x_rand_vals.keys())

    def test_missing_col(self):

        csv = "test_csvs/test_missing_col.csv" # Missing col 'Sample Point Description'
        with self.assertRaises(ValueError):
            load_report(csv)      

    def test_misspelled_col(self):
        
        csv = "test_csvs/test_misspelled_col.csv" # Misspelled col 'Concentration Maximum Stat Base' as "Concentracion Maximum Stat Base"
        with self.assertRaises(ValueError):
            load_report(csv)

    def test_empty_col(self):

        csv = "test_csvs/test_empty_col.csv" # Col 'Mon. Period Start Date' is empty
        with self.assertRaises(ValueError):
            load_report(csv)

class Test_check_clean(unittest.TestCase):
    """
    Test check_clean() functionality for a "good" dictionary and one with a problematic string for datetime conversion.
    """

    def test_good_dict(self):

        this_dict = {
            1211:
            {
                'mon. period start date': '8/1/2016', # no hours, mins
                'dmr parameter description abbrv.': 'Flow, In Conduit or Thru Treatment Plant', 
                'sample point description': ' ', # space for a value
                'reported value concentration avg': '', 
                'concentrated average stat base': '', 
                'reported value concentration max': '13', 
                'concentration maximum stat base': '  0.9 ' # extra spaces before & after
            }
        }
        x = check_clean(this_dict)

        self.assertIsInstance(x, dict) # returns a dict
        self.assertGreater(len(x.keys()), 0) # dict isn't empty

    def test_bad_date(self):
        this_dict = {
            1212:
            {
                'mon. period start date': '8/1/20', # problematic string
                'dmr parameter description abbrv.': '', 
                'sample point description': '',
                'reported value concentration avg': '', 
                'concentrated average stat base': '', 
                'reported value concentration max': '', 
                'concentration maximum stat base': ''
            }
        }

        with self.assertRaises(ValueError):
            check_clean(this_dict)

class Test_get_values(unittest.TestCase):
    """
    Test get_values().
    """

    def test_bad_sample_pt_desc(self):
        # create dict where either the col 'sample point description' doesn't have value of "effluent gross value"
        this_dict = {
            1211:
            {
                'mon. period start date': '8/1/2016',
                'dmr parameter description abbrv.': 'Flow, In Conduit or Thru Treatment Plant', 
                'sample point description': '', # missing val
                'reported value concentration avg': '', 
                'concentrated average stat base': '', 
                'reported value concentration max': '13', 
                'concentration maximum stat base': '0.9'
            }
        }
        x = get_values(this_dict)
        
        self.assertIsInstance(x, dict) # returns a dict
        self.assertGreater(len(x.keys()), 0) # dict isn't empty       

    def test_short_input(self):
        pass

class Test_export_values(unittest.TestCase):
    """
    Test export_values().
    """
    pass

unittest.main(verbosity=2)
