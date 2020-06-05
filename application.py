import os
from flask import Flask, render_template, session, request, redirect
import requests
from flask_bcrypt import Bcrypt
from flask_session import Session
from sqlalchemy import create_engine
import bcrypt
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Check for environment variable

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#secret key
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

# index/home page #
@app.route("/")
def home():
    
    books = db.execute("SELECT * from books limit 10").fetchall()
    return render_template("home.html", books = books)

# login page #
@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/account")
def account():
    return render_template("account.html")

# signup/register page #
@app.route("/register")
def register():
    return render_template("register.html")


# review page to display review of each book #
@app.route("/review/<int:book_id>/isbn")
def review(book_id):
    if session.get('username'):
        username=session.get('username')
        #book_id=request.args["book_id"]
        if db.execute("SELECT * from review WHERE id = :id", {"id": book_id}).rowcount==0:
            return render_template("error.html", message = "No review for this book yet")
        book_review = db.execute("SELECT * from review WHERE id = :id", {"id": book_id}).fetchall()
        books = db.execute("SELECT * from books WHERE id = :id", {"id": book_id}).fetchall()
        #res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "vm2J835rJxnEYd3tH5MJLQ", "isbns": "0062076108"})
        #print(res.json())
    return render_template("review.html", message = book_review, books=books, username=username)


# login user code. this will lead a user to his account#
@app.route("/submit", methods=["POST"])
def submit():
    
    u_name = request.form['username']
    u_pwd = request.form['password']


    if db.execute("SELECT * from users WHERE username = :username  AND password = :password", {"username": u_name, "password": u_pwd}).rowcount==1:
        fetch_user=db.execute("SELECT * FROM users WHERE username = :username  AND password = :password", {"username": u_name, "password": u_pwd}).fetchall()
        for user in fetch_user:
            session['username']= user.username
            accountBooks = db.execute("SELECT * FROM books LIMIT 10").fetchall()
            return render_template("account.html", message="Login Successful", books=accountBooks, u_username=session['username'])  
    else:
        return render_template("error.html", message = "Please login with correct credentials")



# signup/register code. this will take users back to login page after successful registration#
@app.route("/user_signup", methods=["POST"])
def user_signup():
   
    u_email = request.form['email']
    u_name = request.form['username']
    u_pwd = request.form['password']
    u_pwd2 = request.form['password2']
    #print(u_email, u_name, u_pwd, u_pwd2)
    #if u_email == '' or u_name == '' or u_pwd == '' or u_pwd2 == '':
    #    return render_template('register.html', message='Please enter required fields')
    if u_pwd != u_pwd2:
        return render_template('register.html', message='Password must match')
    u_pwd_hash = bcrypt.generate_password_hash('u_pwd')
    #u_pwd_hash_check = bcrypt.check_password_hash(u_pwd_hash, 'pwd')
    #print(u_pwd_hash)     
    if db.execute("SELECT email, username from users WHERE email = :email  AND username= :username", {"email": u_email, "username": u_name}).rowcount != 0:
        return render_template('login.html', message='User already exist, Please Login instead')
       
    else:
        db.execute("INSERT INTO users (email, username, password) VALUES(:email, :username, :password)", {"email": u_email, "username": u_name, "password": u_pwd_hash})
        db.commit()
        return render_template('login.html', message='You have been registered successfully, please login to review your favorite books')
   
# page for review form #
@app.route("/review_form", methods=["GET"])
def review_form():
    if session.get('username'):
        username=session.get('username')
        book_id=request.args["book_id"]
        book_title=request.args["book_title"]
        return render_template("review_form.html", book_id=book_id, book_title=book_title, username=username) 
    else:
        return render_template('login.html', message='please login first') 

# submit review to database #
@app.route("/submit_review", methods=["POST"])
def submit_review():
    b_id = request.form['id']
    b_name = request.form['username']
    b_rev = request.form['review']
    #b_title = request.form['title']     
    db.execute("INSERT INTO review (id, username, review) VALUES(:id, :username, :review)", { "id": b_id, "username": b_name, "review": b_rev })
    db.commit()
    return render_template('account.html', message='please login first')

@app.route("/submit_search")
def submit_search():
    search_words = request.args['search_words']   
    sql =  """SELECT * FROM books WHERE  title  LIKE '%{}%' OR author  LIKE '%{}%' OR isbn  LIKE '%{}%'""".format(search_words,search_words,search_words)
    db_search = db.execute(sql).fetchall()
    return render_template('account.html', each_book=db_search)
        