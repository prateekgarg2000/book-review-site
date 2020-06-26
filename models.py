import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class user(db.Model):
    __tablename__="users"
    uid=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(20),unique=True)
    password=db.Column(db.String(20),nullable=False)
    def add_rev(self,data,stars,book_obj):
        new_rev=reviews(data=data,starts=stars,book_id=book_obj.isbn,user_id=self.uid)
        book_obj.rev_count=book_obj.rev_count+1
        book_obj.rev_stars=book_obj.rev_stars+stars
        db.session.add(new_rev)
        db.session.commit()

class book(db.Model):
    __tablename__="books"
    isbn=db.Column(db.String(10),primary_key=True)
    title=db.Column(db.String(40),nullable=False)
    author=db.Column(db.String(40),nullable=False)
    year=db.Column(db.Integer,nullable=False)
    rev_count=db.Column(db.Integer,default=0)
    rev_stars=db.Column(db.Integer,default=0)

class review(db.Model):
    __tablename__="reviews"
    rid=db.Column(db.Integer,primary_key=True)
    data=db.Column(db.String,nullable=False)
    stars=db.Column(db.Integer,nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.uid"), nullable=False)
    book_id = db.Column(db.String(10), db.ForeignKey("books.isbn"), nullable=False)
