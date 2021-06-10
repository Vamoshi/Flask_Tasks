from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date
from sqlalchemy.types import DateTime

Base = declarative_base()


class Users(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    user_steps = relationship("Child", back_populates="Users")
    user_sleep = relationship("Child", back_populates="Users")
    user_activity_calories = relationship("Child", back_populates="Users")


class UserSteps(Base):
    __tablename__ = "UserSteps"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    steps = Column(Integer)
    date = Column(Date)
    parent = relationship("Parent", back_populates="UserSteps")


class UserSleep(Base):
    __tablename__ = "UserSleep"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    total_minutes_asleep = Column(Integer)
    total_time_in_bed = Column(Integer)
    date = Column(Date)
    parent = relationship("Parent", back_populates="UserSleep")


class UserCalories(Base):
    __tablename__ = "UserCalories"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('Users.user_id'))
    bmr = Column(Integer)
    calories_total = Column(Integer)
    date = Column(Date)
    parent = relationship("Parent", back_populates="UserCalories")


class FitbitUsers(Base):
    __tablename__ = "FitbitUsers"

    fitbit_user_id = Column(String(60), primary_key=True)
    access_token = Column(Text)
    expires_in = Column(Integer)
    refresh_token = Column(Text)
    scope = Column(Text)
    time_fetched = Column(DateTime)


class Result():
    # Not part of the database
    def __init__(self, status=200, result=None, message=""):
        self.status = status
        self.result = result
        self.message = message
