#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI']= 'postgres://postgres:admin@localhost:5432/fyyur'

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String())
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    create_time = db.Column(db.DateTime, nullable=False)
    
    show = db.relationship('Show', backref='venues')
    
    

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    create_time = db.Column(db.DateTime, nullable=False)
    
    show = db.relationship('Show', backref='artists')
    
    

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    data={}
    venues=[]
    artists=[]
    recent_venues=Venue.query.with_entities(Venue.id, Venue.name, Venue.image_link).order_by(db.desc(Venue.create_time)).limit(5)
    for recent_venue in recent_venues:
        venue={}
        venue['id']=recent_venue.id
        venue['name']=recent_venue.name
        venue['image_link']=recent_venue.image_link
        venues.append(venue)
    
    recent_artists=Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).order_by(db.desc(Artist.create_time)).limit(5)
    for recent_artist in recent_artists:
        artist={}
        artist['id']=recent_artist.id
        artist['name']=recent_artist.name
        artist['image_link']=recent_artist.image_link
        artists.append(artist)
    
    data['venues']=venues
    data['artists']=artists
    return render_template('pages/home.html', data=data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data=[]
    cities=Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
    
    for city in cities:
        c={}
        c['city']=city[1]
        c['state']=city[2]
        venues=[]
        city_venues = Venue.query.filter_by(city=c['city'], state=c['state']).order_by(db.desc(Venue.create_time)).all()
        for ven in city_venues:
            venue={}
            venue['id']=ven.id
            venue['name']=ven.name
            venue["num_upcoming_shows"]=0
            venue_shows=Show.query.filter_by(venue_id=venue['id']).all()
            if len(venue_shows)>0:
                for venue_show in venue_shows:
                    if venue_show.start_time>datetime.now():
                        venue["num_upcoming_shows"] += 1
            venues.append(venue)
        c['venues']=venues
        data.append(c)
            
    '''    
        data=[{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
            "id": 1,
            "name": "The Musical Hop",
            "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
        }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
            }]
        }]
    '''
    return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term=request.form['search_term']
    results=Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike('%'+ search_term +'%')).order_by(db.desc(Venue.create_time)).all()
    
    count=0
    data=[]
    
    for result in results:
        count += 1
        v={}
        v['id']=result.id
        v['name']=result.name
        v['num_upcoming_shows']=0
        venue_shows=Show.query.filter_by(venue_id=v['id']).all()
        if len(venue_shows)>0:
            for venue_show in venue_shows:
                if venue_show.start_time>datetime.now():
                    v['num_upcoming_shows'] += 1
        data.append(v)
        
    
    response={
        "count": count, 
        "data": data
    }
    
    '''
    response={
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    '''
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data={}
    venue=Venue.query.filter_by(id=venue_id).first()
    data['id']=venue.id
    data['name']=venue.name
    genres=venue.genres
    genres=genres.replace('{','')
    genres=genres.replace('}','')
    genres=genres.split(',')
    data['genres']=genres
    data['address']=venue.address
    data['city']=venue.city
    data['state']=venue.state
    data['phone']=venue.phone
    data['website']=venue.website
    data['facebook_link']=venue.facebook_link
    data['image_link']=venue.image_link
    data['seeking_talent']=venue.seeking_talent
    data['seeking_description']=venue.seeking_description
    data['past_shows']=[]
    data['upcoming_shows']=[]
    data['past_shows_count']=0
    data['upcoming_shows_count']=0
    venue_shows=Show.query.filter_by(venue_id=data['id']).all()
    if len(venue_shows)>0:
        for venue_show in venue_shows:
            s={}
            s['artist_id']=venue_show.artist_id
            artist=Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).filter_by(id=s['artist_id']).first()
            s['artist_name']=artist.name
            s['artist_image_link']=artist.image_link
            s['start_time']=venue_show.start_time
            if s['start_time']<datetime.now():
                data['past_shows'].append(s)
                data['past_shows_count'] += 1
            else:
                data['upcoming_shows'].append(s)
                data['upcoming_shows_count'] += 1
    
    '''
    data1={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
        "past_shows": [{
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2={
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3={
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [{
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
            }],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }
    data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
    '''
    return render_template('pages/show_venue.html', venue=data)
    

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
    error=False
    try:
        if len(Venue.query.all())>0:
            id = Venue.query.order_by('id').all()[-1].id + 1
        else:
            id = 1
            
        if request.form['seeking_talent']=='True':
            s=True
        else:
            s=False
            
        seeking_description=''
        if 'talent_description' in request.form.keys():
            seeking_description=request.form['talent_description']
            
        v = Venue(id=id, name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'], genres=request.form.getlist('genres'), image_link=request.form['image_link'], facebook_link=request.form['facebook_link'], website=request.form['website'], seeking_talent=s, seeking_description=seeking_description, create_time=datetime.now() )
        db.session.add(v)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('The new Venue could not be listed!')
        
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error=False
    try:
        venue=Venue.query.get(venue_id)
        name=venue.name
        Show.query.filter_by(venue_id=venue_id).delete()
        db.session.delete(venue)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully deleted!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('The Venue could not be deleted!')

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data=[]
    artists=Artist.query.with_entities(Artist.id, Artist.name).order_by(db.desc(Artist.create_time)).all()
    for artist in artists:
        a={}
        a['id']=artist.id
        a['name']=artist.name
        data.append(a)
    
    '''
    data=[{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]
    '''
    return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term=request.form['search_term']
    results=Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike('%'+ search_term +'%')).order_by(db.desc(Artist.create_time)).all()
    
    count=0
    data=[]
    
    for result in results:
        count += 1
        a={}
        a['id']=result.id
        a['name']=result.name
        a['num_upcoming_shows']=0
        artist_shows=Show.query.filter_by(artist_id=a['id']).all()
        if len(artist_shows)>0:
            for artist_show in artist_shows:
                if artist_show.start_time>datetime.now():
                    a['num_upcoming_shows'] += 1
        data.append(a)
        
    
    response={
        "count": count, 
        "data": data
    }

    '''
    response={
        "count": 1,
        "data": [{
            "id": 4,
            "name": "Guns N Petals",
            "num_upcoming_shows": 0,
        }]
    }
    '''
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data={}
    artist=Artist.query.filter_by(id=artist_id).first()
    data['id']=artist.id
    data['name']=artist.name
    genres=artist.genres
    genres=genres.replace('{','')
    genres=genres.replace('}','')
    genres=genres.split(',')
    data['genres']=genres
    data['city']=artist.city
    data['state']=artist.state
    data['phone']=artist.phone
    data['website']=artist.website
    data['facebook_link']=artist.facebook_link
    data['image_link']=artist.image_link
    data['seeking_venue']=artist.seeking_venue
    data['seeking_description']=artist.seeking_description
    data['past_shows']=[]
    data['upcoming_shows']=[]
    data['past_shows_count']=0
    data['upcoming_shows_count']=0
    artist_shows=Show.query.filter_by(artist_id=data['id']).all()
    if len(artist_shows)>0:
        for artist_show in artist_shows:
            s={}
            s['venue_id']=artist_show.venue_id
            venue=Venue.query.with_entities(Venue.id, Venue.name, Venue.image_link).filter_by(id=s['venue_id']).first()
            s['venue_name']=venue.name
            s['venue_image_link']=venue.image_link
            s['start_time']=artist_show.start_time
            if s['start_time']<datetime.now():
                data['past_shows'].append(s)
                data['past_shows_count'] += 1
            else:
                data['upcoming_shows'].append(s)
                data['upcoming_shows_count'] += 1
    '''
    data1={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "past_shows": [{
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
            "start_time": "2019-05-21T21:30:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data2={
        "id": 5,
        "name": "Matt Quevedo",
        "genres": ["Jazz"],
        "city": "New York",
        "state": "NY",
        "phone": "300-400-5000",
        "facebook_link": "https://www.facebook.com/mattquevedo923251523",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "past_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [],
        "past_shows_count": 1,
        "upcoming_shows_count": 0,
    }
    data3={
        "id": 6,
        "name": "The Wild Sax Band",
        "genres": ["Jazz", "Classical"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "432-325-5432",
        "seeking_venue": False,
        "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "past_shows": [],
        "upcoming_shows": [{
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 0,
        "upcoming_shows_count": 3,
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
    '''
    
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist={}
    a=Artist.query.filter_by(id=artist_id).first()
    artist['id']=a.id
    artist['name']=a.name
    artist['genres']=a.genres
    artist['state']=a.state
    artist['city']=a.city
    artist['phone']=a.phone
    artist['website']=a.website
    artist['facebook_link']=a.facebook_link
    artist['seeking_venue']=a.seeking_venue
    artist['seeking_description']=a.seeking_description
    artist['image_link']=a.image_link
    
    '''
    artist={
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    '''
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    error=False
    try:
        row=Artist.query.get(artist_id)
        if request.form['seeking_venue']=='True':
            s=True
        else:
            s=False
        
        seeking_description=''
        if 'seeking_description' in request.form.keys():
            seeking_description=request.form['seeking_description']
        
        row.name=request.form['name']
        row.city=request.form['city']
        row.state=request.form['state']
        row.phone=request.form['phone']
        row.genres=request.form.getlist('genres')
        row.image_link=request.form['image_link']
        row.facebook_link=request.form['facebook_link']
        row.website=request.form['website']
        row.seeking_venue=s
        row.seeking_description=seeking_description
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' data was successfully updated!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('The Artist data could not be updated!')
    
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue={}
    v=Venue.query.filter_by(id=venue_id).first()
    venue['id']=v.id
    venue['name']=v.name
    venue['genres']=v.genres
    venue['address']=v.address
    venue['state']=v.state
    venue['city']=v.city
    venue['phone']=v.phone
    venue['website']=v.website
    venue['facebook_link']=v.facebook_link
    venue['seeking_talent']=v.seeking_talent
    venue['talent_description']=v.seeking_description
    venue['image_link']=v.image_link
    
    '''
    venue={
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    '''
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    error=False
    try:
        row=Venue.query.get(venue_id)
        if request.form['seeking_talent']=='True':
            s=True
        else:
            s=False
        
        seeking_description=''
        if 'talent_description' in request.form.keys():
            seeking_description=request.form['talent_description']
        
        row.name=request.form['name']
        row.city=request.form['city']
        row.state=request.form['state']
        row.phone=request.form['phone']
        row.address=request.form['address']
        row.genres=request.form.getlist('genres')
        row.image_link=request.form['image_link']
        row.facebook_link=request.form['facebook_link']
        row.website=request.form['website']
        row.seeking_talent=s
        row.seeking_description=seeking_description
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' data was successfully updated!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('The Venue data could not be updated!')
    
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    error=False
    try:
        if len(Artist.query.all())>0:
            id = Artist.query.order_by('id').all()[-1].id + 1
        else:
            id = 1
            
        if request.form['seeking_venue']=='True':
            s=True
        else:
            s=False
            
        seeking_description=''
        if 'seeking_description' in request.form.keys():
            seeking_description=request.form['seeking_description']
            
        a = Artist(id=id, name=request.form['name'], city=request.form['city'], state=request.form['state'], phone=request.form['phone'], genres=request.form.getlist('genres'), image_link=request.form['image_link'], facebook_link=request.form['facebook_link'], website=request.form['website'], seeking_venue=s, seeking_description=seeking_description, create_time=datetime.now() )
        db.session.add(a)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
        flash('The Artist could not be listed!')

    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    data=[]
    shows=Show.query.order_by(db.desc(Show.start_time)).all()
    for show in shows:
        d={}
        d['venue_id']=show.venue_id
        venue_name=Venue.query.with_entities(Venue.id, Venue.name).filter_by(id=d['venue_id']).first()
        d['venue_name']=venue_name.name
        d['artist_id']=show.artist_id
        artist_name=Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).filter_by(id=d['artist_id']).first()
        d['artist_name']=artist_name.name
        d['artist_image_link']=artist_name.image_link
        d['start_time']=show.start_time
        data.append(d)
        
    '''
    data=[{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    '''
    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    error=False
    try:
        if len(Show.query.all())>0:
            id = Show.query.order_by('id').all()[-1].id + 1
        else:
            id = 1
            
        s = Show(id=id, venue_id=request.form['venue_id'], artist_id=request.form['artist_id'], start_time=request.form['start_time'] )
        db.session.add(s)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
        
    if not error:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    else:
        # TODO: on unsuccessful db insert, flash an error instead.
        # e.g., flash('An error occurred. Show could not be listed.')
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
        flash('The new Show could not be listed!')

    return redirect(url_for('index'))

@app.route('/shows/search', methods=['POST'])
def search_shows():
    search_term=request.form['search_term'].lower()
    results=Show.query.order_by(db.desc(Show.start_time)).all()
    
    count=0
    data=[]
    
    for result in results:
        venue=Venue.query.with_entities(Venue.id, Venue.name).filter_by(id=result.venue_id).first()
        artist=Artist.query.with_entities(Artist.id, Artist.name, Artist.image_link).filter_by(id=result.artist_id).first()
        if search_term in venue.name.lower() or search_term in artist.name.lower():
            count += 1
            r={}
            r['venue_id']=result.venue_id
            r['venue_name']=venue.name
            r['artist_id']=result.artist_id
            r['artist_name']=artist.name
            r['artist_image']=artist.image_link
            r['start_time']=result.start_time
            data.append(r)
        
    
    response={
        "count": count, 
        "data": data
    }
    
    '''
    response={
        "count": 1,
        "data": [{
            "id": 2,
            "name": "The Dueling Pianos Bar",
            "num_upcoming_shows": 0,
        }]
    }
    '''
    return render_template('pages/search_shows.html', results=response, search_term=request.form.get('search_term', ''))

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
