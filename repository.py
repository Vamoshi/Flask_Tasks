import database
from database import SessionLocal


def addUser(userJson):
    try:
        session = SessionLocal()
        database.addUser(session, userJson)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(
            f"Couldn't add user to database \nParameters: \nUserJson: {userJson} \nError:{error}"
        )
    finally:
        session.close()


def getUser(userId):
    try:
        session = SessionLocal()
        result = database.getUser(session, userId)
        session.close()
        return result
    except Exception as error:
        print(error)
        return None


def updateUser(userId, userJson):
    try:
        session = SessionLocal()
        user = database.updateUser(session, userId, userJson)
        session.commit()
        session.close()
        return user
    except Exception as error:
        session.rollback()
        raise Exception(
            f"""
                Couldn't update user record 
                \nParameters: 
                \nUserId:{userId} 
                \nUserJson: {userJson} 
                \nError:{error}
            """
        )
