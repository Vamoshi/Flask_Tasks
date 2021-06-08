from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.types import DateTime

Base = declarative_base()


class Users(Base):
    __tablename__ = "Users"

    user_id = Column(String(60), primary_key=True)
    access_token = Column(Text)
    expires_in = Column(Integer)
    refresh_token = Column(Text)
    scope = Column(Text)
    time_fetched = Column(DateTime)
