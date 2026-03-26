from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    fullname = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)

    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)
    fs_token_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    roles = db.relationship('Role', secondary='user_roles')
    user_reservations = db.relationship('Spotreservation', backref='user')

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255) )  

class UserRoles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))

class Parkinglot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_name= db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    no_of_spots = db.Column(db.Integer)
    status = status = db.Column(db.String(1), nullable=False)


    lot_spots = db.relationship('Parkingspot', backref='parkinglot')
    def __repr__(self):
        return f'<Parkinglot {self.location_name}>'
    
class Parkingspot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey('parkinglot.id'))
    status = db.Column(db.String(1), nullable=False)

    spot_reservations = db.relationship('Spotreservation', backref='reservedspot')

class Spotreservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer, db.ForeignKey('parkingspot.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    vehicle_no = db.Column(db.String(80), nullable=False)
    parking_time = db.Column(db.DateTime, nullable=False)
    leaving_time = db.Column(db.DateTime)
    parking_cost = db.Column(db.Float)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
