from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app = Flask(__name__)
db = SQLAlchemy(app)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime, nullable=False)
    artist_id = db.Column(db.Integer,db.ForeignKey('artist.id'),nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('venue.id'),nullable=False)
    #upcoming = db.Column(db.Boolean, nullable=False, default=True)
    
    def __repr__(self):
      return f'<show {self.id} {self.start_time} v_show {self.venue_id}, a_show {self.artist_id}  >'


class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    genres = db.Column(db.String(120),nullable=False)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    venues = db.relationship('Show', backref='v_show', lazy=True) 
    
    def __repr__(self):
     return f'<venue {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_talent} {self.seeking_description} {self.upcoming_shows_count} {self.past_shows_count}>'
     
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
#########################################DONE############################################
    
class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,default=False)
    seeking_description = db.Column(db.Text)
    upcoming_shows_count = db.Column(db.Integer, default=0)
    past_shows_count = db.Column(db.Integer, default=0)
    artists = db.relationship('Show', backref='a_show', lazy=True)

    def __repr__(self):
      return f'<artist {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.website_link} {self.seeking_venue} {self.seeking_description} {self.upcoming_shows_count} {self.past_shows_count}>'
    