from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# User defined modules
from models import FitbitUsers


SQLALCHEMY_DATABASE_URL = "sqlite:///./db.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# session is for db session
# record should already be an instatiated model
def add(session, record):
    session.add(record)


# session is for db session
# value is what we are searching for
# ModelField is the Model's field that we are comparing to, e.g Users.user_id
# ModelClass is the table we will search the id from, e.g Users
# ModelClass corresponds to a table in the database
def get(session, value, ModelField, ModelClass):
    result = session.query(ModelClass).filter(ModelField == value).first()
    return result


def getAll(session,  ModelClass):
    result = session.query(ModelClass).all()
    return result


def update(session, id, newRecord, ModelId, ModelClass):
    record = session.query(ModelClass).filter(ModelId == id).first()
    record = newRecord
    session.add(record)

    return record


def getAllByField(session, value, ModelClass, ModelField):
    results = session.query(ModelClass).filter(ModelField == value).all()
    return results
