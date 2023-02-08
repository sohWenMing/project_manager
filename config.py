import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'thisisthesecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQL_TRACK_MODIFICATIONS = False
    

