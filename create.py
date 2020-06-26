import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
        db.create_all()

# print(type(x.iloc[0,0]))
# print(type(x.iloc[0,1]))
# print(type(x.iloc[0,2]))
# print(type(x.iloc[0,3]))
