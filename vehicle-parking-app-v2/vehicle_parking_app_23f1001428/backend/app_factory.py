# app_factory.py
from flask import Flask
from flask_security import Security
from models import db, user_datastore
from controllers.config import Config
from flask_caching import Cache

cache = Cache()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cache.init_app(app)
    Security(app, user_datastore)
    
    return app
