from datetime import datetime
from models import FitbitUsers, Result, UserAccessTokens, Users
import database
from database import SessionLocal
import uuid


def addDatabaseRecord(record):
    try:
        session = SessionLocal()
        database.add(session, record)
        session.commit()
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def getByField(value, ModelField, ModelClass):
    try:
        session = SessionLocal()
        result = database.get(session, value, ModelField, ModelClass)
        session.close()

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


def getByFields(filters, ModelClass):
    try:
        session = SessionLocal()
        result = database.getByFields(session, filters, ModelClass)
        session.commit()

        print(f"RESULT IS ===== {result[0]}")
        return Result(
            result=result,
            message="Successfully retrieved data"
        )
    except:
        return Result(
            status_code=500,
            message="Unable to retrieve data"
        )
    finally:
        session.close()


def getAll(ModelClass):
    try:
        session = SessionLocal()
        result = database.getAll(session, ModelClass)
        return result
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()


def getAllByField(value, ModelClass, ModelField):
    try:
        session = SessionLocal()
        results = database.getAllByField(
            session, value, ModelClass, ModelField
        )
        return Result(
            result=results,
            message="Successfully retrieved data"
        )
    except:
        session.rollback()
        raise Exception(f'Failed to retrieve data')
    finally:
        session.close()


def updateFieldByField(value, ModelFieldToUpdate, ModelClass, fieldToQuery, ModelFieldToQuery):
    try:
        session = SessionLocal()
        database.update(
            session, value, ModelFieldToUpdate, ModelClass, fieldToQuery, ModelFieldToQuery
        )
        session.commit()
        return Result(
            status_code=200,
            message="Successfully updated record"
        )
    except:
        session.rollback()
        return Result(
            status_code=409,
            message="Record already exists"
        )
    finally:
        session.close()


def updateUserToken(userId):
    access_token = uuid.uuid4().hex
    try:
        # Update User Access Token
        session = SessionLocal()
        record = database.get(
            session, userId, UserAccessTokens.user_id, UserAccessTokens
        )
        record.access_token = access_token
        database.add(session, record)
        session.commit()
        return access_token
    except:
        session.rollback()
        try:
            # Creates UserAccessToken record if it doesn't exist
            session = SessionLocal()
            record = UserAccessTokens(
                user_id=userId,
                access_token=access_token
            )
            database.add(session, record)
            session.commit()
            return access_token
        except:
            session.rollback()
            raise Exception("Couldn't create User Access Token record")
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
                message="Email and password match",
                status_code=201
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


def checkUserToken(userId, access_token):
    try:
        session = SessionLocal()
        record = database.get(
            session, userId, UserAccessTokens.user_id, UserAccessTokens
        )
        if(record is None):
            return Result(
                status_code=404,
                message="Record not found"
            )
    except Exception as error:
        session.rollback()
        raise Exception(f'Error:{error}')
    finally:
        session.close()

    # Check that received access_token == fetched access_token
    # If different, return error
    if(record.access_token != access_token):
        return Result(
            status_code=403,
            message="Error: Access Tokens do not match"
        )

    return Result(
        message="Tokens match",
        result=record
    )
