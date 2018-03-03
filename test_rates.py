# test_rates.py
import unittest
import os
import json
from app import create_app

class RatesTestCase(unittest.TestCase):
    """This class represents the ratestask test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

    # my smoke test
    def test_api_can_get_prices(self):
        """Test API can get a single rate by using it's id."""
        result = self.client().get(
            'rates?getprices=1')
        self.assertEqual(result.status_code, 200)
        self.assertIn('CNSGH', str(result.data))

    def test_api_can_get_rates_by_id(self):
        """Test API can get a single rate by using it's id."""
        result = self.client().get(
            'rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 200)
        self.assertIn('CNSGH', str(result.data))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
