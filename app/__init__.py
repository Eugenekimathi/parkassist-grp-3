from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from marshmallow import ValidationError
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
db = SQLAlchemy()
