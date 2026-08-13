"""Flask application bootstrapper registering blueprints and starting the server."""

from __future__ import annotations
import os
from flask import Flask

# Blueprints
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.students import students_bp
from .routes.attendance import attendance_bp
from .routes.analytics import analytics_bp
from .routes.assistant import assistant_bp
from .routes.assessments import assessments_bp
from .routes.wellness import wellness_bp
from .routes.reports import reports_bp
from .routes.settings import settings_bp


def create_app() -> Flask:
    app = Flask(__name__)
    
    # Session encryption key
    app.secret_key = os.environ.get("FLASK_SECRET_KEY", "pmla_scwe_v2_secret_key_12345")

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(assistant_bp)
    app.register_blueprint(assessments_bp)
    app.register_blueprint(wellness_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    @app.context_processor
    def inject_notifications():
        from core import notification_service
        try:
            cnt = notification_service.get_unread_notification_count()
        except Exception:
            cnt = 0
        return {"unread_cnt": cnt}

    return app


def run_web_server():
    app = create_app()
    host = os.environ.get("FLASK_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    print(f"Flask Web Server active at http://{host}:{port}/")
    print("Press Ctrl+C to stop.")
    app.run(host=host, port=port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    run_web_server()
