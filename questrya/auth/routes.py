"""
LAYER: routes
ROLE: API enpoints
CAN communicate with: Services, Schemas
MUST NOT communicate with: Domain, Repositories, ORM models

This must have all the API endpoints
"""

from datetime import timedelta

from flask import Blueprint, request
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)

from questrya.common.schemas import (
    GenericClientResponseError,
    GenericServerResponseError,
)
from questrya.auth.schemas import (
    LoginRequest,
    LoginResponseSuccess,
    TokenRefreshResponseSuccess,
)
from questrya.auth.service import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login
    ---
    tags:
      - JWT Auth
    parameters:
      - name: email
        type: string
        required: true
      - name: password
        type: string
        required: true
    responses:
      200:
        description: JWT temporary access token & JWT long-live refresh token
      400:
        description: client error
      500:
        description: server error
    """
    data = request.get_json()
    try:
        validated_data = LoginRequest.model_validate(data)

        access_token, refresh_token = auth_service.authenticate(
            email=validated_data.email, password=validated_data.password
        )
        return (
            LoginResponseSuccess(
                access_token=access_token, refresh_token=refresh_token
            ).model_dump(),
            200,
        )
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500


@auth_bp.route('/token/new', methods=['POST'])
@jwt_required(refresh=True)  # Requires a refresh token
def token_refresh():
    """
    Get a new JWT temporary access token (expires in 1 hour)
    ---
    tags:
      - JWT Auth
    responses:
      200:
        description: JWT temporary access token
    """
    try:
        identity = get_jwt_identity()
        new_access_token = create_access_token(
            identity=identity, expires_delta=timedelta(hours=1)
        )
        return (
            TokenRefreshResponseSuccess(access_token=new_access_token).model_dump(),
            200,
        )
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500
