# app/__init__.py

# existing import remains
from flask_api import FlaskAPI

# local import
from instance.config import app_config

from flask import request, jsonify, json, abort

import psycopg2
from psycopg2.extras import RealDictCursor

    #####################
    # existing code remains #
    #####################
def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    @app.route('/rates', methods=['GET'])
    def rates():
        global conn, query
        if request.method == "GET":
            # GET
            results = []

            # parsing get request arguments
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            origin = request.args.get('origin')
            destination = request.args.get('destination')

            # Try to connect
            try:
                query = """SELECT * FROM prices WHERE (day BETWEEN %s AND %s)
                            AND (orig_code = %s OR orig_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR orig_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s)))
                            AND (dest_code = %s OR dest_code IN (SELECT code FROM ports WHERE parent_slug = %s)
                              OR dest_code IN (SELECT code FROM ports WHERE parent_slug IN
                                (SELECT slug FROM regions WHERE parent_slug = %s)))"""
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute(query,(date_from, date_to, origin, origin, origin, destination, destination, destination))

                obj = json.dumps(cur.fetchall(), indent=2)
                results.append(obj)
            except:
                print
                "I am unable to connect to the database."

            response = jsonify(results)
            response.status_code = 200
            return response

    return app