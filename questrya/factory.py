import os

from flask import Flask
from questrya.extensions import (
    init_celery,
    init_db,
    init_swagger,
    init_bcrypt,
    init_jwt,
)

PKG_NAME = os.path.dirname(os.path.realpath(__file__)).split('/')[-1]


# pylint: disable=import-outside-toplevel
def create_app():
    app = Flask(PKG_NAME)

    init_swagger(app)

    init_db(app)

    init_celery(app)

    init_bcrypt(app)

    init_jwt(app)

    from questrya.api import register_blueprints

    register_blueprints(app)
    return app
