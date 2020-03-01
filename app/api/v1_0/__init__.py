from flask import Blueprint

api = Blueprint("api", __name__)

import app.api.v1_0.views
