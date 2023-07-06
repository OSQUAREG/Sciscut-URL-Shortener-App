from flask import Blueprint

auth_bp = Blueprint("auth", __name__, template_folder="templates")

users_bp = Blueprint("users", __name__, template_folder="templates")

links_bp = Blueprint("links", __name__, template_folder="templates")
