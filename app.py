#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from operator import itemgetter
import re
from sqlalchemy.exc import SQLAlchemyError
from distutils.command.sdist import show_formats
import sys
import json
import dateutil.parser
import babel
from flask import Flask, abort, jsonify, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
#from flask_wtf import FlaskForm
from sqlalchemy import func, true
from forms import *
from flask_migrate import Migrate
from datetime import datetime
from dateutil.parser import parse
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
#SQLALCHEMY_DATABASE_URI = 'postgresql://*****:****@localhost:5432/artist_booking'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

app.secret_key = 'super secret key'
#app.config['SESSION_TYPE'] = 'filesystem'
# TODO: connect to a local postgresql database
migration = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

#########################################DONE##########################################################################
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: Done ** replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  #venues = Venue.query.with_entities(Venue.id, Venue.name).all()
  areas = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  data = []

  for area in areas:
    area_venues = Venue.query.filter_by(state=area.state).filter_by(city=area.city).all()
    venue_data = []
    for venue in area_venues:
      venue_data.append({
        "id": venue.id,
        "name": venue.name, 
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.utcnow()).all())
      })
    data.append({
      "city": area.city,
      "state": area.state, 
      "venues": venue_data
    })

  return render_template('pages/venues.html', areas=data)
   
  
 #########################################DONE##########################################################################

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: Done ** implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  results = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form['search_term']))).all()
  response={
    "count": len(results),
    "data": []
    }
  for venue in results:
    response["data"].append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.utcnow()).all()),
      })
  
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))
 


   
#########################################DONE##########################################################################

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  #past_show_query = db.session.query(Show).filter(Show.venue = Venue.query.get(venue_id) == venue = Venue.query.get(venue_id), Show.start_time <= datetime.utcnow()).order_by(Show.start_time).all()
  #upcoming_show_query = db.session.query(Show).filter(Show.venue = Venue.query.get(venue_id) == venue = Venue.query.get(venue_id), Show.start_time >= datetime.utcnow()).order_by(Show.start_time).all()
  form = VenueForm()
  past_show_query = Show.query.filter(Show.venue_id == venue_id, Show.start_time <= datetime.utcnow()).order_by(Show.start_time).all()
  upcoming_show_query = Show.query.filter(Show.venue_id == venue_id, Show.start_time >= datetime.utcnow()).order_by(Show.start_time).all()
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  try:
    if(past_show_query is not None):    
      for p_show in past_show_query:
        show_info = {
          "artist_id": p_show.artist_id,
          "artist_name": Artist.query.get(p_show.artist_id).name,
          "artist_image_link":  Artist.query.get(p_show.artist_id).image_link,
          "start_time": str(p_show.start_time)
        }
        past_shows.append(show_info)

    if(upcoming_show_query is not None):
      for u_show in upcoming_show_query:
        show_info = {
          "artist_id": u_show.artist_id,
          "artist_name": Artist.query.get(u_show.artist_id).name,
          "artist_image_link":  Artist.query.get(u_show.artist_id).image_link,
          "start_time": str(u_show.start_time)
        }
        upcoming_shows.append(show_info)

    data={
      "id": venue_id,
      "name": venue.name,
      "genres": venue.genres.split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_venue.html', venue=data)  
  except SQLAlchemyError as e:
      #error = str(e.__dict__['orig'])
      #flash( error)
      print(f'Exception "{e}" in create_venue_submission()')
      flash('An error occurred')
      db.session.rollback()
  finally:
        db.session.close()    
  
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
#########################################DONE##########################################################################  

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  new_venue = Venue()
  new_venue.name = request.form.get('name').strip()
  new_venue.address =request.form.get('address')
  new_venue.genres = request.form.getlist('genres')
  new_venue.city = request.form.get('city')
  new_venue.state =request.form.get('state')
  phone =request.form.get('phone')
  new_venue.phone = re.sub('\D', '', phone) 
  new_venue.facebook_link =request.form.get('facebook_link').strip()
  new_venue.image_link =request.form.get('image_link').strip()
  new_venue.website_link =request.form.get('website_link').strip()
  new_venue.seeking_talent = True if request.form.get('seeking_talent') == 'y' else False
  new_venue.seeking_description = request.form.get('seeking_description') 
  new_venue.upcoming_shows_count = 0
  new_venue.past_shows_count = 0
  
  # Redirect back to form if errors in form validation
  if not form.validate():
    flash( form.errors )
    flash('An error occurred. name ' + new_venue.genres + ' could not be validate.')
    return render_template('pages/home.html')
  else:
    try:
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + new_venue.name + ' was successfully listed!')
      return render_template('pages/home.html')
    except SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash( error)
      print(f'Exception "{e}" in create_venue_submission()')
      flash('An error occurred. Venue ' + new_venue.name + ' could not be listed.')
      db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')    
  
#########################################DONE##########################################################################
  
  # on successful db insert, flash success
  #flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  #return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  #venue_id = request.form.get('venue_id')
  error = False
  try:
    venue = Venue.query.filter(Venue.id == venue_id)
    #venue = Venue.query.get(venue_id)
    db.session.remove(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error: 
    flash(f'An error occurred. Venue {venue_id} could not be deleted.')
  if not error: 
    flash(f'Venue {venue_id} was successfully deleted.')
  return render_template('pages/home.html')
  

#########################################DONE##########################################################################
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=artists)
#########################################DONE########################################################################## 

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
 
  results = db.session.query(Artist).filter(Artist.name.ilike('%{}%'.format(request.form['search_term']))).all()
  #results = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
  response={
    "count": len(results),
    "data": []
    }
  for artist in results:
    response["data"].append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": len(db.session.query(Show).filter(Show.artist_id == artist.id).filter(Show.start_time > datetime.utcnow()).all()),
      })
    
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
  
  
#########################################DONE##########################################################################

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id 
  
  #past_show_query = db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time <= datetime.utcnow()).order_by(Show.start_time).all()
  #upcoming_show_query = db.session.query(Show).filter(Show.artist_id == artist_id, Show.start_time >= datetime.utcnow()).order_by(Show.start_time).all()
  
  #past_show_query = Show.query.filter(Show.artist_id == artist_id, Show.start_time < datetime.utcnow()).order_by(Show.start_time).all()
  #upcoming_show_query = Show.query.filter(Show.artist_id == artist_id, Show.start_time > datetime.utcnow()).order_by(Show.start_time).all()
  past_show_query = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time<=datetime.now()).all() 
  upcoming_show_query = db.session.query(Show).filter(Show.artist_id == artist_id).filter(Show.start_time>=datetime.now()).all() 
  artist = Artist.query.get(artist_id)
  #shows = artist.shows
  past_shows = []
  upcoming_shows = []
  try:
    if(past_show_query is not None):    
      for p_show in past_show_query:
        show_info = {
          "venue_id": p_show.venue_id,
          "venue_name": Venue.query.get(p_show.venue_id).name,
          "venue_image_link": Venue.query.get(p_show.venue_id).image_link,
          "start_time": str(p_show.start_time)
        }
        past_shows.append(show_info)

    if(upcoming_show_query is not None):
      for u_show in upcoming_show_query:
        show_info = {
          "venue_id": u_show.venue_id,
          "venue_name": Venue.query.get(u_show.venue_id).name,
          "venue_image_link": Venue.query.get(u_show.venue_id).image_link,
          "start_time": str(u_show.start_time)
        }
        upcoming_shows.append(show_info)

    data = {
      "id": artist_id,
      "name": artist.name,
      "genres": artist.genres.split(','), 
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description":artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows)
    }
    return render_template('pages/show_artist.html', artist=data)   
  except SQLAlchemyError as e:
    error = str(e.__dict__['orig'])
    flash( error)
    print(f'Exception "{e}" in create_venue_submission()')
    flash('An error occurred')
    db.session.rollback()
  finally:
    db.session.close()
  
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
#########################################DONE##########################################################################
#  delete artist
#  ----------------------------------------------------------------
@app.route('/artists/delete', methods=['POST'])
def delete_artist():
  artist_id = request.form.get('artist_id')
  deleted_artist = Artist.query.filter(Artist.id == artist_id)
  artistName = deleted_artist.name
  try:
    #db.session.delete(deleted_artist)
    db.session.remove(deleted_artist)
    db.session.commit()
    flash('Artist ' + artistName + ' was successfully deleted!')
  except:
    db.session.rollback()
    flash('please try again. Venue ' + artistName + ' could not be deleted.')
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))
  #########################################DONE##########################################################################
#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_edit = Artist.query.get(artist_id)
  if artist_edit: 
    form.name.data = artist_edit.name
    form.city.data = artist_edit.city
    form.state.data = artist_edit.state
    form.phone.data = artist_edit.phone
    form.genres.data = artist_edit.genres
    form.facebook_link.data = artist_edit.facebook_link
    form.image_link.data = artist_edit.image_link
    form.website_link.data = artist_edit.website_link
    form.seeking_venue.data = artist_edit.seeking_venue
    form.seeking_description.data = artist_edit.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>    
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist_edit)
#########################################DONE##########################################################################
@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm()
  #update_artist = Artist.query.filter(Artist.id == artist_id)
  update_artist = Artist.query.get(artist_id)
  update_artist.name = request.form.get('name').strip()
  update_artist.city = request.form.get('city')
  update_artist.state =  request.form.get('state')
  update_artist.phone =  request.form.get('phone')
  update_artist.genres =  request.form.getlist('genres', str)
  update_artist.facebook_link =  request.form.get('facebook_link').strip()
  update_artist.image_link =  request.form.get('image_link').strip()
  update_artist.website_link =  request.form.get('website_link').strip()
  update_artist.seeking_venue =  True if request.form.get('seeking_venue') == 'y' else False
  update_artist.seeking_description =  request.form.get('seeking_description')
  if not form.validate():
    flash( form.errors )
    flash('An error occurred. Artist could not be validate.')
    return render_template('pages/home.html')
  else:
    try:
      db.session.merge(update_artist)
      db.session.commit()
      flash('Artist ' + update_artist.name + ' successfully Updated')  
      return redirect(url_for('show_artist', artist_id=artist_id))
    except SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash( error)
      print(f'Exception "{e}" in create_venue_submission()')
      db.session.rollback()
      flash('An error occurred. Artist ' + update_artist.name + ' could not be listed.')
    finally:
      db.session.close()       
      return redirect(url_for('show_artist', artist_id=artist_id))
#########################################DONE##########################################################################
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue_edit = Venue.query.get(venue_id)
  if venue_edit: 
    form.name.data = venue_edit.name
    form.city.data = venue_edit.city
    form.state.data = venue_edit.state
    form.address.data = venue_edit.address
    form.phone.data = venue_edit.phone
    form.genres.data = venue_edit.genres
    form.facebook_link.data = venue_edit.facebook_link
    form.image_link.data = venue_edit.image_link
    form.website_link.data = venue_edit.website_link
    form.seeking_talent.data = venue_edit.seeking_talent
    form.seeking_description.data = venue_edit.seeking_description
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue_edit)

#########################################DONE##########################################################################
@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  #error = False 
  form = VenueForm() 
  update_venue = Venue.query.get(venue_id)
  update_venue.name = request.form.get('name').strip()
  update_venue.address =  request.form.get('address')
  update_venue.city = request.form.get('city')
  update_venue.state =  request.form.get('state')
  update_venue.phone =  request.form.get('phone')
  update_venue.genres =  request.form.getlist('genres', str)
  update_venue.facebook_link =  request.form.get('facebook_link').strip()
  update_venue.image_link =  request.form.get('image_link').strip()
  update_venue.website_link =  request.form.get('website_link').strip()
  update_venue.seeking_talent =  True if request.form.get('seeking_talent') == 'y' else False
  update_venue.seeking_description =  request.form.get('seeking_description')
  
  if not form.validate():
    flash( form.errors )
    flash('An error occurred. Venue could not be validate.')
    return render_template('pages/home.html')
  else:
    try:
      #db.session.execute(update_venue)
      db.session.merge(update_venue)
      db.session.commit()
      flash('Venue ' + update_venue.name + ' successfully Updated') 
      return redirect(url_for('show_venue', venue_id=venue_id)) 
    except SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash( error)
      print(f'Exception "{e}" in create_venue_submission()')
      db.session.rollback()
      flash('An error occurred. Venue ' + update_venue.name + ' could not be listed.')
    finally:
      db.session.close()       
      return redirect(url_for('show_venue', venue_id=venue_id))


  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
#########################################DONE##########################################################################  

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  new_artist = Artist()
  new_artist.name = request.form.get('name').strip()
  new_artist.genres = request.form.getlist('genres',str)
  new_artist.city = request.form.get('city')
  new_artist.state = request.form.get('state')
  phone = request.form.get('phone')
  new_artist.phone = re.sub('\D', '', phone) 
  new_artist.facebook_link =request.form.get('facebook_link').strip()
  new_artist.image_link =request.form.get('image_link').strip()
  new_artist.website_link =request.form.get('website_link').strip()
  new_artist.seeking_venue = True if request.form.get('seeking_venue') == 'y' else False
  new_artist.seeking_description = request.form.get('seeking_description') 
  new_artist.upcoming_shows_count = 0
  new_artist.past_shows_count = 0
  
  # Redirect back to form if errors in form validation
  if not form.validate():
    flash( form.errors )
    flash('An error occurred. name ' + new_artist.name + ' could not be validate.')
    return render_template('pages/home.html')
  else:
    try:
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + new_artist.name + ' was successfully listed!')
      return render_template('pages/home.html')
    except SQLAlchemyError as e:
      error = str(e.__dict__['orig'])
      flash( error)
      print(f'Exception "{e}" in create_venue_submission()')
      flash('An error occurred. Artist ' + new_artist.name + ' could not be listed.')
      db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')
#########################################DONE##########################################################################
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  # num_shows should be aggregated based on number of upcoming shows per venue.
  upcoming_show_list = Show.query.filter(Show.start_time >= datetime.utcnow()).order_by(Show.start_time).all()
  #shows_list = Show.query.all()
  data = []
  if(upcoming_show_list):
    for show in upcoming_show_list:
      data.append({
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
      })
  return render_template('pages/shows.html', shows=data)
#########################################DONE##########################################################################
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)
#########################################DONE##########################################################################
  
@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()
  new_show = Show()
  new_show.artist_id = request.form.get('artist_id')
  new_show.venue_id = request.form.get('venue_id')
  new_show.start_time = request.form.get('start_time')
  show_time = parse(new_show.start_time)
  # Redirect back to form if errors in form validation
  if not form.validate():
    flash( form.errors )
    flash('An error occurred. show could not be validate.')
    return render_template('pages/home.html')
  else:
    try:
      db.session.add(new_show)
      #db.session.commit()
      updated_artist = Artist.query.get(new_show.artist_id)
      updated_venue = Venue.query.get(new_show.venue_id)

      #if new_show.start_time.strptime() > parse(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')):
      if show_time > datetime.utcnow():
        updated_artist.upcoming_shows_count = int(updated_artist.upcoming_shows_count + 1) 
        updated_venue.upcoming_shows_count = int(updated_venue.upcoming_shows_count + 1)

      #elif new_show.start_time.strptime() < parse(datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')): 
      elif show_time < datetime.utcnow():
        updated_artist.past_shows_count = int(updated_artist.past_shows_count + 1)
        updated_venue.past_shows_count = int(updated_venue.past_shows_count + 1)
      
      db.session.merge(updated_artist)
      db.session.merge(updated_venue)
      db.session.commit()
      #flash('upcoming show artist -' + str(updated_artist.upcoming_shows_count) + 'and venue-' + str(updated_venue.upcoming_shows_count))
      #flash('Past show artist -' + str(updated_venue.past_shows_count) + 'and venue-' + str(updated_venue.past_shows_count))
      flash('New show was successfully listed!')
      return render_template('pages/home.html')
    except SQLAlchemyError as e:
      print(f'Exception "{e}" in create_venue_submission()')
      flash('An error occurred. Show could not be listed.')
      db.session.rollback()
    finally:
        db.session.close()
    return render_template('pages/home.html')

#########################################DONE##########################################################################
  

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
