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
        global conn
        if request.method == "GET":
            # GET
            results = []

            # Try to connect

            try:
                conn = psycopg2.connect("host='127.0.0.1' dbname='postgres' user='postgres' password=''")
                # conn = psycopg2.connect('dbname=postgres')
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute("""SELECT * FROM prices""")
                obj = json.dumps(cur.fetchall(), indent=2)
            except:
                print
                "I am unable to connect to the database."


            # cur = conn.cursor()

            # obj = json.dumps(cur.fetchall(), indent=2)

            #obj = {
            #     'orig_code': 'CNSGH',
            #     'dest_code': 'EETLL',
            #     'day': '2016-01-01',
            #     'price': '1244'
            #}
            results.append(obj)

            response = jsonify(results)
            response.status_code = 200
            return response

    return app