import os

# grab the folder containing script
basedir = os.path.abspath(os.path.dirname(__file__))

# config
DATABASE = 'flasktaskr.db'
DEBUG = True
#USERNAME = 'admin'
#PASSWORD = 'admin'
WTF_CSRF_ENABLED = True
SECRET_KEY = 'bishuguessedit'

# define the full path for the database
DATABASE_PATH = os.path.join(basedir, DATABASE)

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH