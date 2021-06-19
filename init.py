from flask import Flask, config
from . import config
import models
from database import engine


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_CONNECTION_URI
    app.app_context().push()
    models.Base.metadata.create_all(bind=engine)
    return app
