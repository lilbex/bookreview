from sqlalchemy import MetaData, Table, Column, String, Integer
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy as db 

class Database():
    # replace the user, password, hostname and database according to your configuration according to your information
    engine = db.create_engine('postgresql://postgres:2345@localhost/bookReview')
 

class Books(Base):
    """Model for customer account."""
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(200), unique=True)
    title = db.Column(db.String(200))
    author = db.Column(db.Integer)
    year = db.Column(db.Text())
    
def __init__(self, customer, dealer, rating, comments):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        
   