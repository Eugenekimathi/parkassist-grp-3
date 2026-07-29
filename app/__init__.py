from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name="development"):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models import(
        Estate, Court, Checkpoint, User, Resident, Visitor,
        Vehicle, CheckpointLog, ParkingSlot, ParkingRecord,
        BlockingIncident, Notification, MovementHistory
    )

    return app
