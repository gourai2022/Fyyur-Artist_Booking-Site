import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

# TODO IMPLEMENT DATABASE URL

#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_DATABASE_URI = 'postgresql://***:*****@localhost:5432/artist_booking'
#SQLALCHEMY_TRACK_MODIFICATIONS = False