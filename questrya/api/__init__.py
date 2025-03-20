from flask import Blueprint

def register_blueprints(app):
    """Registers all blueprints for the API."""
    from questrya.users.routes import users_bp
    from questrya.auth.routes import auth_bp

    app.register_blueprint(users_bp, url_prefix="/api/users")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

api_blueprint = Blueprint("api", __name__)
