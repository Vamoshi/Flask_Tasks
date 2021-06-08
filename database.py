from sqlalchemy import create_engine, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# User defined modules
from models import Users


SQLALCHEMY_DATABASE_URL = "sqlite:///./user.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def addUser(session, userJson):
    record = Users(
        user_id=userJson["user_id"],
        access_token=userJson["access_token"],
        expires_in=userJson["expires_in"],
        refresh_token=userJson["refresh_token"],
        scope=userJson["scope"],
        time_fetched=datetime.now(),
    )

    # record = Users(
    #     user_id=id,
    #     name=name
    # )

    session.add(record)


def getUser(session, userId):
    try:
        result = session.query(Users).filter(Users.user_id == userId).first()

        print('GETTING USER')
        print("RESULT IS ", result)
        return result
    except:
        return None


def updateUser(session, userId, userJson):
    user = session.query(Users).filter(Users.user_id == userId).first()

    user.access_token = userJson["access_token"],
    user.expires_in = userJson["expires_in"],
    user.refresh_token = userJson["refresh_token"],
    user.scope = userJson["scope"],
    user.time_fetched = datetime.now

    session.add(user)

    return user