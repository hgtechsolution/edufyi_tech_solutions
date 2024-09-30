from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    encryption_password = db.Column(db.String(60), nullable=False)
    town = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)


    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.email}')"

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(30), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    encryption_password = db.Column(db.String(60), nullable=False)
    town = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)


    def __repr__(self):
        return f"Admin('{self.id}','{self.username}', '{self.email}')"

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(40),nullable=False)
    url = db.Column(db.String(100),nullable=False)
    course_category = db.Column(db.String(100),nullable=False)


class Encry_Key(db.Model):
    __tablename__ = 'encry_key'  # This defines the table name in the database
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(255), unique=True, nullable=False)  # Example column
    key_type = db.Column(db.String(255), nullable=True)  # Example column

    # def __repr__(self):
    #     return f"Key('{self.key_value}', '{self.description}')"



