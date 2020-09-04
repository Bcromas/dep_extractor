import unittest
import random
from extract_report_values import *

class Test_load_report(unittest.TestCase):

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

unittest.main()
