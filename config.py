import os
# from flask_sqlalchemy import SQLAlchemy

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:f1T30Km5cAZdjDOpA295MT7C5@localhost:3306/xcodata"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://xcodata:2103.MontP!@85.215.33.219:3306/xcodata"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False