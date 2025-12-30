#this is the flask app instance that creates the app object as an instance of the class Flask imported from the flask package

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

#create the extension
db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config) #this loads the configuration setting from the Config class in config.py
    db.init_app(app) #this initializes the SQLAlchemy object with the flask app instance
    migrate.init_app(app, db) #this sets up database migration support for the app using Flask-Migrate

    # Move the import to the very end to avoid circular import issues
    from Backend import models