#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    # columns to be added after second upgrade file
    genres = db.Column(db.String())
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    # column to be added after third upgrade file
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

    # columns to be added after second upgrade file
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    # column to be added after third upgrade file
    create_time = db.Column(db.DateTime, nullable=False)
    
    show = db.relationship('Show', backref='artists')
    
    

# table to be added after second upgrade file
class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)