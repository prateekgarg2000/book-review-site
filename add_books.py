import pandas as pd
import os

from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db=SQLAlchemy(app)

x=pd.read_csv("books.csv")
for i in range(len(x)):
    if(i%50==0):
        print(i,end=" ")
    book_obj=book(isbn=x.iloc[i,0],title=x.iloc[i,1],author=x.iloc[i,2],year=int(x.iloc[i,3]),rev_count=0,rev_stars=0)
    db.session.add(book_obj)

db.session.commit()
