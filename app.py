# Modules
from datetime import datetime
from flask import Flask, request
from urllib import parse
import requests
import json
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from werkzeug.security import generate_password_hash, check_password_hash

# User defined modules
from repository import *
from utilities import base64EncodeSecrets, tokenNeedRefresh
from models import FitbitUsers,  UserCalories, UserSleep, UserSteps, Users
import models
from fitbitCalls import *
from database import engine

# URLS
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"
redirect_url = f"{flask_base_url}/fitbit/code"
parsed_redirect_url = parse.quote_plus(redirect_url)
fitbit_api_url = "https://api.fitbit.com"

# These strings below are used to access fitbit endpoints
# e.g api.fitbit.com  "/1/user/-"  /activities/date/{date}.json
# This is standardized in fitbit endpoints, so I decided to make them variables to access them easily
user_1_url = "1/user/-"
user_1_1_url = "1.1/user/-"
user_1_2_url = "1.2/user/-"

# Authorization parameters
scope = 'activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight'
expires_in = 604800

# Fitbit Application Secrets:
client_id = "23B8ZW"
client_secret = "262f6c5c63a9eecc269982e70a2b5c3e"


# initialize database
models.Base.metadata.create_all(bind=engine)
# initalize app + auth
app = Flask(__name__)

# create auths
basicAuth = HTTPBasicAuth()
tokenAuth = HTTPTokenAuth(scheme="Bearer")
multiAuth = MultiAuth(basicAuth, tokenAuth)


# Auth decorators
@basicAuth.verify_password
def verify_password(username, password):
    userQuery = getOneByField(username, Users.email, Users)
    # check if username and password are passed

    if(username is not None and password is not None):
        if(userQuery.result is not None and check_password_hash(userQuery.result.password, password)):
            return userQuery.result
        # User is not found
        return True
    # Failed auth
    return None


@tokenAuth.verify_token
def verify_token(token):
    userTokenRecordQuery = getOneByField(
        token, UserAccessTokens.access_token, UserAccessTokens
    )
    # check if token is passed
    if(token is not None and token != ""):
        if(userTokenRecordQuery.result is not None):
            if(userTokenRecordQuery.result.access_token == token):
                # TODO: Check if token has not expired
                return userTokenRecordQuery.result
        # token does not exist
        return True
    # Failed auth
    return None


@app.route('/')
def index():
    return f"<h1>THIS IS THE INDEX</h1>"


@app.route('/v1/users', methods=['POST'])
@multiAuth.login_required
def users():
    if(multiAuth.current_user() is not None and type(multiAuth.current_user()) is not str):
        # Login credentials via credentials in Bearer
        if(type(multiAuth.current_user()) is Users):
            # Update user token
            userAccessToken = updateUserToken(basicAuth.current_user().user_id)
            return json.dumps({
                "status_code": 200,
                "message": "user exists",
                "user_id": basicAuth.current_user().user_id,
                "access_token": userAccessToken
            })

        # Login via auth token
        return json.dumps({
            "status_code": 200,
            "message": "token exists",
            "user_id": tokenAuth.current_user().user_id,
        })

    # Register
    fromUser = request.json
    try:
        email = fromUser['email']
        password = fromUser['password']
    except:
        email = None
        password = None

    if(email is not None and password is not None):
        # get user if user in database
        response = getOneByField(email, Users.email, Users)
        # user does not exist in database
        if(response.status_code == 404):
            record = Users(
                email=email,
                password=generate_password_hash(password)
            )
            result = addDatabaseRecord(record)

            return json.dumps({
                "status_code": result.status_code,
                "message": result.message
            })

        # user exists in database
        else:
            jsonDict = [None]
            if(response.status_code == 200):
                jsonDict[0] = {
                    "status_code": response.status_code,
                    "user_id": -1,
                    "message": "User already exists"
                }
            # Something went wrong in database
            else:
                jsonDict[0] = {
                    "status_code": response.status_code,
                    "user_id": -1,
                    "message": response.message
                }

            return json.dumps(jsonDict[0])

    return json.dumps({
        "message": "Error: Bad request",
        "status_code": 400
    })


@app.route('/v1/fitbitconsent', methods=['POST'])
@tokenAuth.login_required
# Returns url for fitbit consent page
def fitbitConsent():
    fromUser = request.json
    try:
        userId = fromUser['user_id']
    except:
        return json.dumps({
            "status_code": 400
        })

    # TODO: Check if fitbit token needs refresh
    # return empty string if doesn't need refresh or has been refreshed
    # else return fitbit consent page url

    return f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={parsed_redirect_url}&scope={scope}&state={userId}"


@ app.route('/v1/fitbitauthcode', methods=['POST', 'GET'])
# Get Auth code from fitbit redirect url then exchange for access token
def fitbitAuthCode():
    print("Was able to get Authorization code!")
    # Get Auth code from url
    code = request.args.get('code')
    userId = request.args.get('state')

    print(f"PASSED STATE IS===={userId}\n")

    # Encode 'client_id:client_secret' to base64
    encoded_secret = base64EncodeSecrets(client_id, client_secret)

    # Exchange Authorization code for fitbit access_token
    req = requests.post(
        token_base_url,
        headers={
            'Authorization': f'Basic {encoded_secret}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }, params={
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_url,
        }
    )

    # get response as json
    fitbitUserJson = req.json()

    # If an error is returned by fitbit api
    if(req.status_code != 200):
        return f"""
        <div style="min-height: 100vh; display: grid; place-items: center;">
            <h1>SOMETHING WENT WRONG! <br/>
                {fitbitUserJson}
            </h1>
        </div>
        """

    fitbitUserId = fitbitUserJson["user_id"]

    # get user & fitbitUser
    fitbitUser = getOneByField(
        fitbitUserId, FitbitUsers.fitbit_user_id, FitbitUsers
    )

    try:
        if(fitbitUser.result is None):
            print("Fitbit user doesn't exist, adding to db!")
            record = FitbitUsers(
                fitbit_user_id=fitbitUserJson['user_id'],
                user_id=userId,
                access_token=fitbitUserJson['access_token'],
                expires_in=fitbitUserJson['expires_in'],
                refresh_token=fitbitUserJson['refresh_token'],
                scope=fitbitUserJson['scope'],
                time_fetched=datetime.now(),
            )
            addDatabaseRecord(record)

        # if fitbit user record already exists, update it
        elif(
            fitbitUserJson['access_token'] != fitbitUser.result.access_token or
            fitbitUserJson['refresh_token'] != fitbitUser.result.refresh_token
        ):
            print("tokens are different, updating user!")
            updateFitbitUser(fitbitUserJson['user_id'], fitbitUserJson)

        date = "2020-08-08"

        accessToken = fitbitUserJson["access_token"]

        # Add data to database
        addFitbitSleep(
            userId,
            accessToken,
            fitbit_api_url,
            user_1_2_url,
            date
        )
        addFitbitSteps(
            userId,
            accessToken,
            fitbit_api_url,
            user_1_2_url,
            date
        )
        addFitbitCalories(
            userId,
            accessToken,
            fitbit_api_url,
            user_1_2_url,
            date
        )

        return """
                <div style="min-height: 100vh; display: grid; place-items: center;">
                    <h1>SUCCESSFULLY LOGGED IN TO FITBIT! <br/>
                        YOU MAY NOW CLOSE THIS WINDOW!
                    </h1>
                </div>
                """
    except Exception as error:
        return f"""
        <div style="min-height: 100vh; display: grid; place-items: center;">
            <h1>SOMETHING WENT WRONG! <br/>
                {error}
            </h1>
        </div>
        """


@ app.route('/v1/refresh')
# Refresh tokens
def refresh():
    userId = request.json['user_id']
    fitbitUser = getOneByField(userId, FitbitUsers, FitbitUsers.user_id)
    encoded_secret = base64EncodeSecrets(client_id, client_secret)
    req = requests.post(
        token_base_url,
        headers={
            'Authorization': f'Basic {encoded_secret}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }, params={
            'grant_type': 'refresh_token',
            'refresh_token': fitbitUser.refresh_token,
            # expires_in defaults to 28800 or 8 hours
        }
    )

    fitbitUserJson = req.json()

    # If an error is returned by fitbit api
    if(req.status_code != 200):
        raise Exception(f"{req.json()}{fitbitUserJson}")

    updateFitbitUser(fitbitUserJson["user_id"], fitbitUserJson)

    print("REFRESHED TOKEN! USER JSON IS ================ ", fitbitUserJson)

    return ""


# Routes to fetch data

@ app.route('/v1/users/<userId>/sleep', defaults={'sleepId': None})
@ app.route('/v1/users/<userId>/sleep/<sleepId>')
@tokenAuth.login_required
def sleep(userId, sleepId):
    if(userId is None):
        return json.dumps({
            "status_code": 400,
            "message": "Bad request: User Id is missing"
        })
    # No sleepId, so get all sleep records by user
    elif(sleepId is None):
        sleepRecords = getAllByField(userId, UserSleep, UserSleep.user_id)
        sleepJson = {
            "result": [],
            "status_code": 200,
            "user_id": userId
        }

        for record in sleepRecords.result:
            sleepJson["result"].append(
                {
                    "total_minutes_asleep": record.total_minutes_asleep,
                    "total_time_in_bed": record.total_time_in_bed,
                    "date": str(record.date)
                }
            )

        return json.dumps(sleepJson)

    filters = (
        UserSleep.user_id == userId,
        UserSleep.id == sleepId
    )

    sleepQuery = getOneByFields(filters, UserSleep)

    if(sleepQuery.result is not None):
        record = sleepQuery.result
        return json.dumps({
            "status_code": sleepQuery.status_code,
            "result": {
                "total_minutes_asleep": record.total_minutes_asleep,
                "total_time_in_bed": record.total_time_in_bed,
                "date": str(record.date)
            },
            "message": sleepQuery.message
        })

    return json.dumps({
        "status_code": sleepQuery.status_code,
        "result": None,
        "message": sleepQuery.message
    })


@ app.route('/v1/users/<userId>/steps', defaults={'stepsId': None})
@ app.route('/v1/users/<userId>/steps/<stepsId>')
@tokenAuth.login_required
def steps(userId, stepsId):
    if(userId is None):
        return json.dumps({
            "status_code": 400,
            "message": "Bad request: User Id is missing"
        })
    elif(stepsId is None):
        stepsRecords = getAllByField(userId, UserSteps, UserSteps.user_id)
        stepsJson = {
            "result": [],
            "status_code": 200,
            "user_id": userId
        }

        for record in stepsRecords.result:
            stepsJson["result"].append(
                {
                    "steps": record.steps,
                    "date": str(record.date)
                }
            )

        return json.dumps(stepsJson)

    filters = (
        UserSteps.user_id == userId,
        UserSteps.id == stepsId
    )

    stepsQuery = getOneByFields(filters, UserSteps)

    if(stepsQuery.result is not None):
        record = stepsQuery.result

        return json.dumps({
            "status_code": stepsQuery.status_code,
            "result": {
                "steps": record.steps,
                "date": str(record.date)
            },
            "message": stepsQuery.message
        })

    return json.dumps({
        "status_code": stepsQuery.status_code,
        "result": None,
        "message": stepsQuery.message
    })


@ app.route('/v1/users/<userId>/calories', defaults={'caloriesId': None})
@ app.route('/v1/users/<userId>/calories/<caloriesId>')
@tokenAuth.login_required
def calories(userId, caloriesId):
    if(userId is None):
        return json.dumps({
            "status_code": 400,
            "message": "Bad request: User Id is missing"
        })
    elif(caloriesId is None):
        caloriesRecords = getAllByField(
            userId, UserCalories, UserCalories.user_id
        )

        caloriesJson = {
            "result": [],
            "status_code": 200,
            "user_id": userId
        }

        for record in caloriesRecords.result:
            caloriesJson["result"].append(
                {
                    "bmr": record.bmr,
                    "calories_total": record.calories_total,
                    "date": str(record.date)
                }
            )

        return json.dumps(caloriesJson)

    filters = (
        UserCalories.user_id == userId,
        UserCalories.id == caloriesId
    )

    caloriesQuery = getOneByFields(filters, UserCalories)

    if(caloriesQuery.result is not None):
        record = caloriesQuery.result
        return json.dumps({
            "status_code": caloriesQuery.status_code,
            "result": {
                "bmr": record.bmr,
                "calories_total": record.calories_total,
                "date": str(record.date)
            },
            "message": caloriesQuery.message
        })

    return json.dumps({
        "status_code": caloriesQuery.status_code,
        "result": None,
        "message": caloriesQuery.message
    })


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# http://192.168.100.6:5000/
