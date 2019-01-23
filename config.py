#encoding: utf-8
import os

DEBUG = True

SECRET_KEY = os.urandom(24)

SQLALCHEMY_DATABASE_URI = 'mysql://libo:123567@localhost/testdb'
SQLALCHEMY_TRACK_MODIFICATIONS = True


