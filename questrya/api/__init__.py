from flask import Blueprint


def register_blueprints(app):
    """Registers all blueprints for the API."""
    from questrya.users.routes import users_bp
    from questrya.auth.routes import auth_bp
    from questrya.monitor.routes import monitor_bp

    app.register_blueprint(users_bp, url_prefix='/api/users')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(monitor_bp, url_prefix='/api/monitor')


api_blueprint = Blueprint('api', __name__)
