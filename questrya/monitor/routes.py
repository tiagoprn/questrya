"""
LAYER: routes
ROLE: API enpoints
CAN communicate with: Services, Schemas
MUST NOT communicate with: Domain, Repositories, ORM models

This must have all the API endpoints
"""

from datetime import datetime

import flask
from flask import Blueprint

from questrya.common.schemas import (
    GenericClientResponseError,
    GenericServerResponseError,
)
from questrya.monitor.schemas import (
    LivenessResponseSuccess,
    ReadinessResponseSuccess,
)
from questrya.settings import VERSION

monitor_bp = Blueprint('monitor', __name__)


@monitor_bp.route('/readiness', methods=['GET'])
def readiness():
    """
    Used by k8s, to know when a container is ready.

    The kubelet uses readiness probes to know when a container
    is ready to start accepting traffic.

    A Pod is considered ready when all of its Containers are ready.
    One use of this signal is to control which Pods are used as
    backends for Services.
    When a Pod is not ready, it is removed from Service load balancers.
    This will run ONLY ONCE.
    ---
    tags:
      - Monitor
    responses:
      200:
        description: show the app as ready, with its app version and type.
    """
    try:
        flask_version = flask.__version__
        app_type = f'flask-framework {flask_version}'

        return (
            ReadinessResponseSuccess(
                ready='OK', app_version=VERSION, app_type=f'{app_type}'
            ).model_dump(),
            200,
        )
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500


@monitor_bp.route('/liveness', methods=['GET'])
def liveness():
    """
    Used by k8s, to know if a Container is live.

    The kubelet uses liveness probes to know when to restart a Container. For
    example, liveness probes could catch a deadlock, where an application is
    running, but unable to make progress. Restarting a Container in such a
    state can help to make the application more available despite bugs. This
    will run ON REGULAR INTERVALS.
    ---
    tags:
      - Monitor
    responses:
      200:
        description: show the app as live, with its version
                     and the current timestamp.
    """
    try:
        timestamp = datetime.utcnow().isoformat()
        return (
            LivenessResponseSuccess(
                live='OK', version=VERSION, timestamp=timestamp
            ).model_dump(),
            200,
        )
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500
