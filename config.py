import os

class Config:
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:123456789@localhost/edtech'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = r'C:\Users\shree\Desktop\projects\edtech_website\static\videos'
    MAIL_SERVER = 'mail.epicculinaryexperiences.com'  # Use appropriate mail server
    MAIL_PORT = 587
    MAIL_USERNAME = 'scarlet@epicculinaryexperiences.com'
    MAIL_PASSWORD = 'qJ7fHrS!rs'
    MAIL_USE_TLS = True