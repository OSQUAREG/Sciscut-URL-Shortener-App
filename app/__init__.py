import os
from http import HTTPStatus
from flask import Flask, jsonify, render_template, Blueprint
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from .blocklist import BLOCKLIST
from .models import User, Link, ClickAnalytic
from .utils import db, cache, limiter
from .utils.create_defaults import (
    drop_create_all,
    create_default_admin,
    empty_qr_folder,
    qr_code_folder_path,
)
from .config.config import config_dict
from .views.auth import auth_bp

# from .views.user import user_ns
# from .views.link import links_ns

# from .views.admin import admin_links_ns, admin_users_ns
from flask_login import LoginManager
from flask_admin import Admin, menu
from flask_admin.contrib.sqla import ModelView
from app.admin.admin_views import MyAdminIndexView, MyModelView, LogoutMenuLink
from flask_cors import CORS
from decouple import config


qr_code_folder_path = config("QR_CODE_FOLDER_PATH")


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)
    CORS(app)

    # Initialize flask-admin
    app.config["FLASK_ADMIN_SWATCH"] = "united"
    admin = Admin(
        app,
        name="Admin: Sciscut-URL Shortener App",
        template_mode="bootstrap3",
        index_view=MyAdminIndexView(),
        base_template="my_master.html",
    )

    admin.add_view(MyModelView(User, db.session))
    admin.add_view(MyModelView(Link, db.session))
    admin.add_view(MyModelView(ClickAnalytic, db.session))
    admin.add_link(LogoutMenuLink(name="Logout"))

    # Initialize flask-migrate
    migrate = Migrate(app, db)

    # # Initialize flask-jwt
    jwt = JWTManager(app)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.filter_by(email=identity).one_or_none()

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blacklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "status": 401,
                    "sub_status": 42,
                    "message": "Your login has expired. Please login again.",
                }
            ),
            401,
        )

    # Initialize flask-login
    login_manager = LoginManager(app)

    @login_manager.user_loader
    def load_user(user_id):
        if user_id is None:
            return HTTPStatus.UNAUTHORIZED
        return db.session.query(User).get(user_id)

    app.register_blueprint(auth_bp, url_prefix="/")

    # CUSTOM ERROR HANDLERS
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("500.html"), 500

    @app.route("/home")
    def index():
        return render_template("index.html")

    # Flask Admin Views
    @app.route("/")
    def admin_index():
        return render_template("index.html")

    @app.shell_context_processor
    def make_shell_context():
        return {
            "db": db,
            "User": User,
            "Link": Link,
            "ClickAnalytic": ClickAnalytic,
            "drop_create_all": drop_create_all,
            "create_default_admin": create_default_admin,
            "empty_qr_folder": empty_qr_folder,
            "qr_folder": qr_code_folder_path,
        }

    return app
