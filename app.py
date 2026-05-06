"""
Insider Sentinel - Flask Application Entry Point
"""
from __future__ import annotations

import os
from pathlib import Path

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from backend.routes import api


def create_app() -> Flask:
    """Application factory."""
    app = Flask(
        __name__,
        static_folder=str(Path(__file__).parent / "frontend"),
        static_url_path="",
    )

    # Configuration
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "insider-sentinel-dev-key-change-in-prod")
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

    # CORS — allow all origins in development
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Register API blueprint
    app.register_blueprint(api)

    # ---------------------------------------------------------------------------
    # Frontend static file serving
    # ---------------------------------------------------------------------------

    @app.route("/")
    def index():
        return send_from_directory(app.static_folder, "login.html")

    @app.route("/login")
    def login_page():
        return send_from_directory(app.static_folder, "login.html")

    @app.route("/admin")
    def admin_dashboard():
        return send_from_directory(app.static_folder, "admin_dashboard.html")

    @app.route("/admin/employee/<int:emp_id>")
    def admin_employee_profile(emp_id: int):
        return send_from_directory(app.static_folder, "admin_employee_profile.html")

    @app.route("/admin/reports")
    def admin_reports():
        return send_from_directory(app.static_folder, "admin_reports.html")

    @app.route("/employee")
    def employee_dashboard():
        return send_from_directory(app.static_folder, "employee_dashboard.html")

    @app.route("/employee/activity-log")
    def employee_activity_log():
        return send_from_directory(app.static_folder, "employee_activity_log.html")

    # ---------------------------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------------------------

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"success": False, "error": "Bad request"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"success": False, "error": "Forbidden"}), 403

    @app.errorhandler(404)
    def not_found(e):
        # Try to serve login for unknown routes (SPA fallback)
        try:
            return send_from_directory(app.static_folder, "login.html")
        except Exception:
            return jsonify({"success": False, "error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500

    # ---------------------------------------------------------------------------
    # Request logging middleware
    # ---------------------------------------------------------------------------

    @app.before_request
    def log_request():
        from flask import request
        import logging
        logging.info("%s %s", request.method, request.path)

    return app


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from database_init import init_database

    # Seed database if it doesn't contain any users yet
    try:
        init_database(skip_if_exists=True)
    except Exception as exc:
        print(f"Warning: database init failed: {exc}")

    flask_app = create_app()
    flask_app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=os.environ.get("FLASK_DEBUG", "0") == "1",
    )
