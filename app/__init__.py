# coding:utf8
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pymysql

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.1:3306/logs"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SECRET_KEY"] = 'bc6c782da0124119935f4627417ca55'
app.debug = True
db = SQLAlchemy(app)

from app.api.v1_0 import api as api_blueprint

app.register_blueprint(api_blueprint)
