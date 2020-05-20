import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bbc5d263-4568-4dab-80c0-744f9ccd0fd3'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'steam.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False