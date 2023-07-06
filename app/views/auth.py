from ..webforms import SignupForm, LoginForm
from flask import flash, redirect, url_for, render_template, request
from flask_login import login_user, current_user
from ..blocklist import BLOCKLIST
from ..models import User
from ..utils import cache, limiter
from werkzeug.security import generate_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
)
from ..views import auth_bp
from http import HTTPStatus


# @auth_bp.route("/")
# def home():
#     return render_template("index.html")


@limiter.limit("10/minute")
@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    """Sign up a User"""

    form = SignupForm()
    if request.method == "POST" and form.validate_on_submit:
        if form.validate_email() and form.is_valid_email():
            new_user = User(
                email=form.email.data,
                password_hash=generate_password_hash(form.password.data),
            )
            new_user.save_to_db()
            flash(f"User with email: '{new_user.email}' created successfully!")
            return redirect(url_for("auth.login")), 201

    context = dict(title="Sign Up Page", form=form)
    return render_template("signup.html", **context), 200


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Login a User: Generates JWT Tokens"""

    form = LoginForm()
    if request.methods == "POST" and form.validate_on_submit():
        user = form.get_user()
        if user:
            login_user(user)
        else:
            flash("User not found. Please sign up.")
            return redirect(url_for("auth.login")), 404

    if current_user.is_authenticated:
        return redirect(url_for(".index", user=user)), 200

    context = dict(title="Login Page", form=form)
    return render_template("login.html", **context), 200


# @auth_ns.route("/refresh")
# class TokenRefresh(Resource):
#     @cache.cached(timeout=10)
#     @auth_ns.doc(description="Refresh JWT Access Token")
#     @jwt_required(refresh=True)
#     def post(self):
#         """Refresh JWT Access Token"""
#         identity = get_jwt_identity()
#         access_token = create_access_token(identity=identity)

#         message = f"Refresh successful."
#         response = {
#             "message": message,
#             "access_token": access_token,
#         }
#         return response, HTTPStatus.OK


# @auth_ns.route("/logout")
# class UserLogout(Resource):
#     @limiter.exempt
#     @auth_ns.doc(description="Logout: Block JWT Token")
#     @jwt_required()
#     def post(self):
#         """Logout a User: Block Access Token"""
#         token = get_jwt()
#         jti = token["jti"]
#         BLOCKLIST.add(jti)

#         return {"message": "Logged Out Successfully!"}
