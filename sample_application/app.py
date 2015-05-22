"""
Application factory
"""

import logging.config
from views import UnixTime, PrintArg, ExampleApiUsage
from models import db
from utils import Logging

from flask import Flask
from flask.ext.restful import Api
from flask.ext.discoverer import Discoverer
from flask.ext.consulate import Consul, ConsulConnectionError


def create_app():
    """
    Create the application and return it to the user

    :return: flask.Flask application
    """

    app = Flask(__name__, static_folder=None)
    app.url_map.strict_slashes = False

    logging.config.dictConfig(
        app.config['SAMPLE_APPLICATION_LOGGING_DICTIONARY']
    )

    Consul(app)

    load_config(app)

    api = Api(app)
    api.add_resource(UnixTime, '/time')
    api.add_resource(PrintArg, '/print/<string:arg>')
    api.add_resource(ExampleApiUsage, '/search')

    db.init_app(app)

    logger = Logging(app)

    discoverer = Discoverer(app)

    return app


def load_config(app):
    """
    Loads configuration in the following order:
        1. config.py
        2. local_config.py (ignore failures)
        3. consul (ignore failures)
    :param app: flask.Flask application instance
    :return: None
    """

    app.config.from_pyfile('config.py')

    try:
        app.config.from_pyfile('local_config.py')
    except IOError:
        pass  # todo: log this failure

    try:
        app.extensions['consul'].apply_remote_config()
    except ConsulConnectionError, e:
        pass  # todo: log this failure


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, use_reloader=False)
