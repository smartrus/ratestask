# app/__init__.py

from flask_api import FlaskAPI
from instance.config import app_config
from flask import request, jsonify, json
import psycopg2
from psycopg2.extras import RealDictCursor

from datetime import datetime


###############################
# my exception handling class #
###############################
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

###############
# created app #
###############
def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    ##############################
    # registered my errorhandler #
    ##############################
    @app.errorhandler(InvalidUsage)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    def validate_date(date_text):
        try:
            datetime.strptime(date_text, '%Y-%m-%d')
        except ValueError:
            raise InvalidUsage('Incorrect date format, should be YYYY-MM-DD!', status_code=400)
        return datetime.strptime(date_text, "%Y-%m-%d")

    def validate_attribute(attr, attr_name):
        if attr is None:
            raise InvalidUsage('Please provide ' + attr_name + ' in your request!', status_code=400)
        return attr

    @app.route('/rates', methods=['GET', 'POST'])
    def rates():
        global conn, query
        if request.method == "GET":
            # GET
            results = []

            # parsing get request arguments
            date_from = validate_attribute(request.args.get('date_from'),'date_from')
            date_to = validate_attribute(request.args.get('date_to'), 'date_to')

            # check if date_from less than or equal to date_to
            if validate_date(date_from) > validate_date(date_to):
                raise InvalidUsage('Please check dates range, date_to must not be less than date_from!', status_code=400)

            origin = validate_attribute(request.args.get('origin'), 'origin')
            destination = validate_attribute(request.args.get('destination'), 'destination')

            # Try to connect
            try:
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                cur = conn.cursor(cursor_factory=RealDictCursor)
            except:
                raise InvalidUsage('I am unable to connect to the database!', status_code=500)

            # Try to query
            try:
                query = """SELECT to_char(day, 'YYYY-MM-DD') AS day, to_char(AVG(price),'FM999999999') AS average_price
                            FROM prices WHERE (day BETWEEN %s AND %s)
                            AND (orig_code = %s OR orig_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR orig_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s)))
                            AND (dest_code = %s OR dest_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR dest_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s))) GROUP BY day"""
                cur.execute(query, (date_from, date_to, origin, origin, origin, destination, destination, destination))

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

            # parsing get request arguments
            date_from = validate_attribute(request.form.get('date_from'),'date_from')
            date_to = validate_attribute(request.form.get('date_to'), 'date_to')

            # check if date_from less than or equal to date_to
            if validate_date(date_from) > validate_date(date_to):
                raise InvalidUsage('Please check dates range, date_to must not be less than date_from!', status_code=400)

            origin_code = validate_attribute(request.form.get('origin_code'), 'origin_code')
            destination_code = validate_attribute(request.form.get('destination_code'), 'destination_code')
            price = validate_attribute(request.form.get('price'), 'price')

            # Try to connect
            try:
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                cur = conn.cursor(cursor_factory=RealDictCursor)
            except:
                raise InvalidUsage('I am unable to connect to the database!', status_code=500)

            # Try to connect and POST
            try:
                query = """INSERT INTO prices (day, price, origin_code, destination_code)
                            VALUES (%s, %s, %s, %s)"""
                cur.execute(query, (date_from, price, origin_code, destination_code))

                obj = json.dumps(cur.fetchall(), indent=2)
                results.append(obj)
            except:
                raise InvalidUsage('Something went wrong with a query!',
                                   status_code=500)


            response = jsonify(results)
            response.status_code = 200
            return response

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        raise InvalidUsage("""You tried an incorrect URL path OR method.
                            Please use GET or POST over /rates with correct attributes instead!""",
                            status_code=410)

    return app
