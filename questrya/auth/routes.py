from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from datetime import timedelta
from questrya.auth.service import AuthService

auth_bp = Blueprint("auth", __name__)
auth_service = AuthService()

@auth_bp.route("/login", methods=["POST"])
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
    """
    data = request.get_json()
    try:
        access_token, refresh_token = auth_service.authenticate(data["email"], data["password"])
        return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200
    except ValueError:
        return jsonify({"msg": "Invalid credentials"}), 401

@auth_bp.route("/token/new", methods=["POST"])
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
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity, expires_delta=timedelta(hours=1))
    return jsonify({"access_token": new_access_token}), 200
