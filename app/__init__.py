# app/__init__.py

# existing import remains
from flask_api import FlaskAPI

# local import
from instance.config import app_config

from flask import request, jsonify, abort

    #####################
    # existing code remains #
    #####################
def create_app(config_name):
    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')

    @app.route('/rates', methods=['GET'])
    def rates():
        if request.method == "GET":
            # GET
            results = []

            obj = {
                'orig_code': 'CNSGH',
                'dest_code': 'EETLL',
                'day': '2016-01-01',
                'price': '1244'
            }
            results.append(obj)

            response = jsonify(results)
            response.status_code = 200
            return response

    return app