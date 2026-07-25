from flask import Flask
from app import db
import app.models

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///parking.db"
db.init_app(app)

with app.app_context():
    db.create_all()   