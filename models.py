from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Client(db.Model):
    __tablename__ = "client"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    credit_card = db.Column(db.String(50))
    car_number = db.Column(db.String(10))
    parkings = db.relationship("ClientParking", backref="client", lazy="dynamic")


class Parking(db.Model):
    __tablename__ = "parking"
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    opened = db.Column(db.Boolean, default=True)
    count_places = db.Column(db.Integer, nullable=False)
    count_available_places = db.Column(db.Integer, nullable=False)
    parkings = db.relationship("ClientParking", backref="parking", lazy="dynamic")


class ClientParking(db.Model):
    __tablename__ = "client_parking"
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("client.id"))
    parking_id = db.Column(db.Integer, db.ForeignKey("parking.id"))
    time_in = db.Column(db.DateTime, default=db.func.now())
    time_out = db.Column(db.DateTime)
