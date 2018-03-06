# app/__init__.py

from flask_api import FlaskAPI
from instance.config import app_config
from flask import request, jsonify, json
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


# exception handling class
class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


# superclass for rates
class Rate:
    def __init__(self):
        self.date_from = ''
        self.date_to = ''
        self.orig_code = ''
        self.dest_code = ''
        self.price = 0
        self.query = ''

    def set_date_from(self, date_from):
        self.date_from = date_from

    def get_date_from(self):
        return self.date_from

    def set_date_to(self, date_to):
        self.date_to = date_to

    def get_date_to(self):
        return self.date_to

    def set_orig_code(self, orig_code):
        self.orig_code = orig_code

    def get_orig_code(self):
        return self.orig_code

    def set_dest_code(self, dest_code):
        self.dest_code = dest_code

    def get_dest_code(self):
        return self.dest_code

    def set_price(self, price):
        self.price = price

    def get_price(self):
        return self.price

    def set_query(self, query):
        self.query = query

    def get_query(self):
        return self.query


# subclass for Get requests
class RateAnalyst(Rate):
    def __init__(self, date_from, date_to, orig_code, dest_code):
        self.date_from = date_from
        self.date_to = date_to
        self.orig_code = orig_code
        self.dest_code = dest_code
        self.query = """SELECT to_char(day, 'YYYY-MM-DD') AS day, to_char(AVG(price),'FM999999999') AS average_price
                            FROM prices WHERE (day BETWEEN %s AND %s)
                            AND (orig_code = %s OR orig_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR orig_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s)))
                            AND (dest_code = %s OR dest_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR dest_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s))) GROUP BY day"""

# subclass for Post requests
class RateUploader(Rate):
    def __init__(self, date_from, date_to, orig_code, dest_code, price):
        self.date_from = date_from
        self.date_to = date_to
        self.orig_code = orig_code
        self.dest_code = dest_code
        self.price = price
        self.query = 'INSERT INTO prices (day, price, orig_code, dest_code) VALUES'
        self.row = ()

    def date_range(self, start_date, end_date):
        for n in range(int((datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')).days)):
            yield datetime.strptime(start_date, '%Y-%m-%d') + timedelta(n)

    def get_row(self):
        row_tuple = ()
        for single_date in self.date_range(self.date_from, self.date_to):
            row_tuple = row_tuple + (((single_date.strftime("%Y-%m-%d")), self.price, self.orig_code, self.dest_code),)
        self.row = row_tuple
        return self.row

# create app
def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    # register errorhandler
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    def validate_dates(date_from, date_to):
        try:
            datetime.strptime(date_from, '%Y-%m-%d')
        except ValueError:
            raise InvalidUsage('Incorrect date format, should be YYYY-MM-DD!', status_code=400)

        try:
            datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError:
            raise InvalidUsage('Incorrect date format, should be YYYY-MM-DD!', status_code=400)

        if datetime.strptime(date_from, '%Y-%m-%d') > datetime.strptime(date_to, '%Y-%m-%d'):
                raise InvalidUsage('Please check dates range, date_to must not be less than date_from!', status_code=400)

    def validate_attribute(attr, attr_name):
        if attr is None:
            raise InvalidUsage('Please provide ' + attr_name + ' in your request!', status_code=400)
        return attr

    def validate_price(price_text):
        try:
            int(price_text)
        except ValueError:
            raise InvalidUsage('Incorrect price format, should be integer!', status_code=400)

    @app.route('/rates', methods=['GET', 'POST'])
    def rates():
        global conn, query

        if request.method == "GET":
            # GET
            results = []

            # validations
            date_from = validate_attribute(request.args.get('date_from'), 'date_from')
            date_to = validate_attribute(request.args.get('date_to'), 'date_to')
            origin = validate_attribute(request.args.get('origin'), 'origin')
            destination = validate_attribute(request.args.get('destination'), 'destination')
            validate_dates(date_from, date_to)

            rate_a = RateAnalyst(date_from, date_to, origin, destination)

            # Try to connect
            try:
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                cur = conn.cursor(cursor_factory=RealDictCursor)
            except:
                raise InvalidUsage('I am unable to connect to the database!', status_code=500)

            # Try to query
            try:
                cur.execute(rate_a.get_query(), (rate_a.get_date_from(), rate_a.get_date_to(), rate_a.get_orig_code(),
                                                 rate_a.get_orig_code(), rate_a.get_orig_code(), rate_a.get_dest_code(),
                                                 rate_a.get_dest_code(), rate_a.get_dest_code()))

                obj = json.dumps(cur.fetchall(), indent=2)
                results.append(obj)
            except:
                raise InvalidUsage('Something went wrong with a query!', status_code=500)

            response = jsonify(results)
            response.status_code = 200
            return response

        elif request.method == "POST":
            # POST
            results = []

            # validations
            date_from = validate_attribute(request.form.get('date_from'),'date_from')
            date_to = validate_attribute(request.form.get('date_to'), 'date_to')
            origin_code = validate_attribute(request.form.get('origin_code'), 'origin_code')
            destination_code = validate_attribute(request.form.get('destination_code'), 'destination_code')
            price = validate_attribute(request.form.get('price'), 'price')
            validate_dates(date_from, date_to)
            validate_price(request.form.get('price'))

            rate_u = RateUploader(date_from, date_to, origin_code, destination_code, price)

            # Try to connect
            try:
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                cur = conn.cursor()
            except:
                raise InvalidUsage('I am unable to connect to the database!', status_code=500)

            # Try to POST
            try:
                row_data = ','.join((cur.mogrify('(%s,%s,%s,%s)', row)).decode('utf-8') for row in rate_u.get_row())
                cur.execute(rate_u.get_query() + ' ' + row_data)
                conn.commit()

                obj = jsonify({"success": False})
                results.append(obj)

            except psycopg2.DatabaseError as error:
                raise InvalidUsage('Something went wrong with a query! ' + str(error), status_code=500)

            response = jsonify({"success": True})
            response.status_code = 200
            return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        raise InvalidUsage("""You tried an incorrect URL path OR method.
                            Please use GET or POST over /rates with correct attributes instead!""",
                            status_code=410)

    return app
