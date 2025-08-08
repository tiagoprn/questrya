"""
LAYER: routes
ROLE: API enpoints
CAN communicate with: Services, Schemas
MUST NOT communicate with: Domain, Repositories, ORM models

This must have all the API endpoints
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from questrya.common.schemas import (
    GenericClientResponseError,
    GenericServerResponseError,
)
from questrya.users.service import UserService
from questrya.users.schemas import (
    CreateUserRequest,
    CreateUserResponseSuccess,
    GetUserResponseSuccess,
    UpdateUserRequest,
    UpdateUserResponseSuccess,
)

users_bp = Blueprint('users', __name__)
user_service = UserService()


@users_bp.route('/user', methods=['POST'])
def create_user():
    """
    Create a new user
    ---
    tags:
      - Users
    parameters:
      - name: username
        type: string
        required: true
      - name: email
        type: string
        required: true
      - name: password
        type: string
        required: true
    responses:
      201:
        description: created user data.
      400:
        description: client error
      500:
        description: server error
    """
    data = request.get_json()

    try:
        validated_data = CreateUserRequest.model_validate(data)

        user = user_service.register_user(
            validated_data.username,
            validated_data.email,
            validated_data.password,
        )
        return CreateUserResponseSuccess(uuid=user.uuid).model_dump(), 201
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500


@users_bp.route('/user', methods=['PATCH'])
@jwt_required()
def update_user():
    """
    Update user info
    ---
    tags:
      - Users
    parameters:
      - name: email
        type: string
        required: false
      - name: password
        type: string
        required: false
    responses:
      200:
        description: updated user info
      400:
        description: client error
      500:
        description: server error
    """
    data = request.get_json()

    try:
        user_uuid = get_jwt_identity()

        print(f'update_user: user_uuid={user_uuid}')

        validated_data = UpdateUserRequest.model_validate(data)

        user = user_service.update_user(
            user_uuid,
            email=validated_data.email,
            password=validated_data.password,
        )
        return (
            UpdateUserResponseSuccess(
                uuid=user.uuid, email=user.email, password='UPDATED'
            ),
            200,
        )
    except ValueError as e:
        return GenericClientResponseError(error=str(e)).model_dump(), 400
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500


@users_bp.route('/user', methods=['GET'])
@jwt_required()  # with no params, requires the access token (temporary one)
def get_user():
    """
    Get user info
    ---
    tags:
      - Users
    responses:
      200:
        description: user info
      500:
        description: server error
    """
    try:
        user_uuid = get_jwt_identity()
        user = user_service.get_user(user_uuid)
        return (
            GetUserResponseSuccess(
                uuid=user.uuid, email=user.email, username=user.username
            ),
            200,
        )
    except Exception as e:
        return GenericServerResponseError(error=str(e)).model_dump(), 500
