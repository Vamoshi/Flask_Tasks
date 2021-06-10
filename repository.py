from models import Result, Users
import database
from database import SessionLocal


def createUser(email, password):
    try:
        session = SessionLocal()
        record = Users(
            email=email,
            password=password
        )
        database.add(session, record)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(
            f"Email: {email} \nPassword: {password} \nError: {error}"
        )
    finally:
        session.close()


def authenticateUser(email, password):
    try:
        session = SessionLocal()
        user = database.get(session, email, Users.email, Users)
        if(user is None):
            return Result(status=404, message="Email does not exist")
            # return {
            #     "status": 404,
            #     "message": "Email does not exist",
            #     "result": None,
            # }
        elif(password == user.password):
            print("email and password are correct!!")
            return Result(
                result=user,
                message="Email and password match"
            )
        return Result(status=400, message="Password is incorrect")
    except Exception as error:
        print("couldn't get user id")
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def addUser(userJson):
    try:
        session = SessionLocal()
        database.add(session, userJson)
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
        result = database.get(session, userId)
        session.close()
        return result
    except Exception as error:
        print(error)
        return None


def updateUser(userId, userJson):
    try:
        session = SessionLocal()
        user = database.update(session, userId, userJson)
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
