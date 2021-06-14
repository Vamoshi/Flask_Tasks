from datetime import datetime
from models import FitbitUsers, Result, Users
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


def findAndAuthenticateUser(email, password):
    try:
        session = SessionLocal()
        user = database.get(session, email, Users.email, Users)
        if(user is None):
            return Result(status_code=404, message="Email does not exist")
        elif(password == user.password):
            print("email and password are correct!!")
            return Result(
                result=user,
                message="Email and password match"
            )
        return Result(status_code=400, message="Password is incorrect")
    except Exception as error:
        print(error)
        print("couldn't get user id")
        return Result(
            status_code=500,
            message="Bad request"
        )
    finally:
        session.close()


# def addUser(userJson):
#     try:
#         session = SessionLocal()
#         database.add(session, userJson)
#         session.commit()
#     except Exception as error:
#         session.rollback()
#         raise Exception(
#             f"Couldn't add user to database \nParameters: \nUserJson: {userJson} \nError:{error}"
#         )
#     finally:
#         session.close()

def createFitbitUser(userId, fitbitUserJson):
    try:
        session = SessionLocal()
        record = FitbitUsers(
            fitbit_user_id=fitbitUserJson['user_id'],
            user_id=userId,
            access_token=fitbitUserJson['access_token'],
            expires_in=fitbitUserJson['expires_in'],
            refresh_token=fitbitUserJson['refresh_token'],
            scope=fitbitUserJson['scope'],
            time_fetched=datetime.now(),
        )
        database.add(session, record)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def getFitbitUser(userId):
    try:
        session = SessionLocal()
        result = database.get(session, userId)
        session.close()
        return result
    except Exception as error:
        print(error)
        return None


def getByField(value, ModelField, ModelClass):
    try:
        session = SessionLocal()
        result = database.get(session, value, ModelField, ModelClass)
        session.close()

        print(f"RESULT IS ======= {result}")

        if(result is None):
            return Result(
                status_code=404,
                message="record does not exist"
            )

        return Result(
            result=result,
            message="record exists"
        )
    except:
        return Result(
            status_code=400,
            message="bad request"
        )


def getUserAccessToken(userId):
    try:
        session = SessionLocal()
        fitbitUser = database.get(
            session, userId, FitbitUsers.user_id, FitbitUsers)
        return fitbitUser.access_token
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def addRecord(record):
    try:
        session = SessionLocal()
        database.add(session, record)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def getAll(ModelClass):
    try:
        session = SessionLocal()
        result = database.getAll(session, ModelClass)
        return result
    except Exception as error:
        session.rollback
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def updateFitbitUser(fitbitUserId, fitbitUserJson):
    try:
        session = SessionLocal()

        fitbitUser = database.get(
            session, fitbitUserId, FitbitUsers.fitbit_user_id, FitbitUsers
        )
        fitbitUser.access_token = fitbitUserJson['access_token']
        fitbitUser.expires_in = fitbitUserJson['expires_in']
        fitbitUser.refresh_token = fitbitUserJson['refresh_token']
        fitbitUser.scope = fitbitUserJson['scope']
        fitbitUser.time_fetched = datetime.now()

        database.add(session, fitbitUser)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(
            f"""
                Couldn't update Fitbit User record 
                \nParameters: 
                \nUserId:{fitbitUserId} 
                \nUserJson: {fitbitUserJson} 
                \nError:{error}
            """
        )
    finally:
        session.close()
