import os
import requests
from flask import Flask, session,redirect,render_template,request,jsonify,url_for
from flask_session import Session
from sqlalchemy import create_engine,and_
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

# set DATABASE_URL=postgres://wrbwmwbvudftvf:8bccdd0d7f8d28f03b89de75abd40c05ce8df6249338c8348682a33f9730b31e@ec2-35-153-12-59.compute-1.amazonaws.com:5432/d34jftfqov8bpp
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
Session = scoped_session(sessionmaker(bind=engine))
current_user=None
session=Session()


@app.route("/")
def index():
    logged_in=current_user is not None
    return render_template('index.html',logged_in=logged_in)
# @app.route("/api/<string:isbn>")
# def api(isbn):
#     res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "ur6FjansewVteqCOhNfKMQ", "isbns": isbn})
#     return res.json()
@app.route("/logout")
def logout():
    global current_user
    current_user=None
    return redirect(url_for('index'))

@app.route("/register",methods=['GET','POST'])
def register():
    if(request.method=='GET'):
        return render_template("register.html",message="Enter your details")
    name=request.form.get("username")
    password=request.form.get("password")
    if(name==""):
        return render_template("register.html",message="username not entered")
    if(len(password)<5):
        return render_template("register.html",message="small password")

    entry=user.query.filter_by(username=name).all()
    if(len(entry)!=0):
        return render_template("register.html",message="username unavailabale")
    new_user=user(username=name,password=password)

    session.add(new_user)
    session.commit()
    return render_template("success.html",message="registered")

@app.route("/login",methods=['GET','POST'])
def login():
    global current_user
    if(current_user is not None):
        return render_template("index.html",logged_in=1)
    if (request.method=='GET'):
        return render_template("login.html",message="enter details to login")
    name=request.form.get("username")
    password=request.form.get("password")
    entry=user.query.filter_by(username=name).all()
    if len(entry)==0:
        return render_template("login.html",message="username not found");
    if password!=entry[0].password:
        return render_template("login.html",message="wrong password");

    current_user=user.query.filter_by(username=name).one()
    # return render_template("users.html",entries=entries)
    if(current_user is None):
        return render_template("login.html",message="current user not updated")
    else:
        return redirect(url_for('index'))

@app.route("/search",methods=['GET','POST'])
def search():
    if current_user is None:
        return redirect(url_for('index'))
    key=request.form.get("key")
    search_input=request.form.get("search_input")
    search_input='%'+search_input+'%'
    if(key=="isbn"):
        entries=book.query.filter(book.isbn.like(search_input)).all()
    elif(key=="author"):
        entries=book.query.filter(book.author.like(search_input)).all()
    elif(key=="title"):
        entries=book.query.filter(book.title.like(search_input)).all()
    return render_template("search_results.html",entries=entries,length=len(entries))

@app.route("/search/<string:isbn>",methods=['GET','POST'])
def book_details(isbn):
    if(current_user is None):
        return redirect(url_for('index'))
    if request.method=='GET':
        entry=book.query.get(isbn)
        user_review=review.query.filter(and_(review.book_id==isbn,review.user_id==current_user.uid)).all()
        other_reviews=review.query.filter(and_(review.book_id==isbn,review.user_id!=current_user.uid)).all()
        if(len(user_review)!=0):
            return render_template("book_page.html",entry=entry,is_ur=1,user_review=user_review[0],other_reviews=other_reviews);
        else:
            return render_template("book_page.html",entry=entry,is_ur=0,user_review=None,other_reviews=other_reviews);
    data=request.form.get("data")
    stars=request.form.get("rating")
    new_rev=review(data=data,stars=stars,user_id=current_user.uid,book_id=isbn)
    session.add(new_rev)
    session.commit()
    entry=book.query.get(isbn)
    entry.rev_count=entry.rev_count+1
    entry.rev_stars=entry.rev_stars+int(stars)
    session.merge(entry)
    session.flush()
    session.commit()
    return redirect(url_for('book_details',isbn=isbn))

@app.route("/delete_review/<string:isbn>",methods=['POST'])
def delete_review(isbn):
    if(current_user is None):
        return redirect(url_for('index'))

    user_review=review.query.filter(and_(review.book_id==isbn,review.user_id==current_user.uid)).first()
    entry=book.query.get(isbn)
    entry.rev_count=entry.rev_count-1
    entry.rev_stars=entry.rev_stars-user_review.stars
    session.merge(entry)
    session.flush()
    session.commit()
    current_session=session.object_session(user_review)
    current_session.delete(user_review)
    current_session.commit()
    return redirect(url_for('book_details',isbn=isbn))




if __name__=='__main__':
    app.run(debug=True)
