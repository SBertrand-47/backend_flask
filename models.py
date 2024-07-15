from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class House(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False, unique=True)
    rooms = db.relationship('Room', backref='house', lazy=True)

    def __repr__(self):
        return f'<House {self.number}>'

class Room(db.Model):
    __tablename__ = 'rooms'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), nullable=False, unique=True)
    house_id = db.Column(db.Integer, db.ForeignKey('houses.id'), nullable=False)
    occupant = db.relationship('Occupant', uselist=False, backref='room', lazy=True)

    def __repr__(self):
        return f'<Room {self.number} in House {self.house.number}>'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Occupant(db.Model):
    __tablename__ = 'occupants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    registrar_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    registrar = db.relationship('User', backref='registered_occupants')
    room = db.relationship('Room', backref='occupant')

    def __repr__(self):
        return f'<Occupant {self.name} registered by {self.registrar.username} in Room {self.room.number}>'
