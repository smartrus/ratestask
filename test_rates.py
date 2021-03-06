# test_rates.py
import unittest
from app import create_app

class RatesTestCase(unittest.TestCase):
    """This class represents the ratestask test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client

    # my smoke test - do not need it anymore
    # tries to get all the prices and checks if CNSGH is in the returned data
    # def test_api_can_get_prices(self):
    #     """Test API can get all prices."""
    #     result = self.client().get(
    #         'rates?getprices=1')
    #     self.assertEqual(result.status_code, 200)
    #     self.assertIn('CNSGH', str(result.data))

    # a get request from the task description that should be executed successfully
    def test_api_can_get_rates(self):
        """Check a get request from the task description."""
        result = self.client().get(
            'rates?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 200)
        self.assertIn('average_price', str(result.data))
        self.assertIn('2016-01-01', str(result.data))
        self.assertIn('2016-01-10', str(result.data))
        self.assertIn('1142', str(result.data))

    # a get request to the wrong path
    def test_api_with_wrong_path(self):
        """Check a get request to the wrong path."""
        result = self.client().get(
            'rate?date_from=2016-01-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 410)
        self.assertIn('incorrect URL', str(result.data))

    # a get request with no date_from
    def test_api_with_no_date_from(self):
        """Check a get request with no date_from."""
        result = self.client().get(
            'rates?date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide date_from', str(result.data))

    # A get request with no date_to
    def test_api_with_no_date_to(self):
        """Check a get request with no date_to."""
        result = self.client().get(
            'rates?date_from=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide date_to', str(result.data))

    # A get request with no origin
    def test_api_with_no_origin(self):
        """Check a get request with no origin."""
        result = self.client().get(
            'rates?date_from=2016-01-01&date_to=2016-01-10&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide origin', str(result.data))

    # A get request with no destination
    def test_api_with_no_destination(self):
        """Check a get request with no destination."""
        result = self.client().get(
            'rates?date_from=2016-01-01&date_to=2016-01-10&origin=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide destination', str(result.data))

    # A get request with incorrect strings in date_from
    def test_api_with_incorrect_date_from(self):
        """Check a get request with incorrect strings in date_from."""
        result = self.client().get(
            'rates?date_from=2016-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('Incorrect date format', str(result.data))

    # A get request with incorrect strings in date_to
    def test_api_with_incorrect_date_to(self):
        """Check a get request with incorrect strings in date_to."""
        result = self.client().get(
            'rates?date_from=2016-01-01&date_to=2016-010&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('Incorrect date format', str(result.data))

    # A get request with date_to greater than date_from
    def test_api_with_date_to_greater_than_date_from(self):
        """Check a get request with date_to greater than date_from"""
        result = self.client().get(
            'rates?date_from=2016-02-01&date_to=2016-01-10&origin=CNSGH&destination=north_europe_main')
        self.assertEqual(result.status_code, 400)
        self.assertIn('date_to must not be less than date_from', str(result.data))

    # A post request with no date_from
    def test_api_post_with_no_date_from(self):
        """Check a post request with no date_from."""
        result = self.client().post('rates',
                                    data=dict(date_to='2018-02-10',
                                     price='1000', origin_code='CNSGH', destination_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide date_from', str(result.data))

    # A post request with no date_to
    def test_api_post_with_no_date_to(self):
        """Check a post request with no date_to"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', price='1000', origin_code='CNSGH',
                                     destination_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide date_to', str(result.data))

    # A post request with no price
    def test_api_post_with_no_price(self):
        """Check a post request with no price"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', date_to='2018-02-10', origin_code='CNSGH',
                                     destination_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide price', str(result.data))

    # A post request with no origin_code
    def test_api_post_with_no_origin_code(self):
        """Check a post request with no origin_code"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', date_to='2018-02-10', price='1000',
                                     destination_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide origin_code', str(result.data))

    # A post request with no destination_code
    def test_api_post_with_no_destination_code(self):
        """Check a post request with no destination_code"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', date_to='2018-02-10', price='1000',
                                     origin_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('provide destination_code', str(result.data))

    # A post request with wrong price
    def test_api_post_with_wrong_price(self):
        """Check a post request with wrong price"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', date_to='2018-02-10', price='100xx',
                                     origin_code='CNSGH', destination_code='CNSGH'))
        self.assertEqual(result.status_code, 400)
        self.assertIn('Incorrect price', str(result.data))

    # A post request to insert data
    def test_api_post_insert(self):
        """Check a post request to insert data"""
        result = self.client().post('rates',
                                    data=dict(date_from='2018-02-01', date_to='2018-02-10', price='1000',
                                     origin_code='CNSGH', destination_code='CNSGH'))
        self.assertEqual(result.status_code, 200)
        self.assertIn('true', str(result.data))

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
