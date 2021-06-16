# Modules
from datetime import datetime
from flask import Flask, redirect, request, url_for
from urllib import parse
import requests
from werkzeug.wrappers import response

# User defined modules
from database import engine
from repository import addRecord, checkUserToken, createFitbitUser, findAndAuthenticateUser, createUser, getAll, getAllByField, getByField, getFitbitUser, getUserAccessToken, updateFitbitUser, updateUserToken
from utilities import base64EncodeSecrets, tokenNeedRefresh
from models import FitbitUsers, UserAccessTokens, UserCalories, UserSleep, UserSteps, Users
import models
import json
from fitbitCalls import *

app = Flask(__name__)

# URLS
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"
redirect_url = f"{flask_base_url}/fitbit/code"
parsed_redirect_url = parse.quote_plus(redirect_url)
fitbit_api_url = "https://api.fitbit.com"
user_1_url = "1/user/-"
user_1_1_url = "1.1/user/-"
user_1_2_url = "1.2/user/-"
scope = 'activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight'
expires_in = 604800
# http://127.0.0.1:5000
#

# # # Fitbit Application Secrets:
client_id = "23B8ZW"
client_secret = "262f6c5c63a9eecc269982e70a2b5c3e"


class Mutable:
    # For debugging/development
    # Replace userId with userId from flutter application,
    # then access the rest of the fields by looking up the database
    # only keep route
    userId = None
    fitbitUserId = ""
    route = ""
    accessToken = ""


# initiate database engine
models.Base.metadata.create_all(bind=engine)


@app.route('/')
def index():
    return "<h1>THIS IS THE INDEX</h1>"


@app.route('/test/users', methods=["POST", "GET"])
def users():
    users = getAll(Users)

    usersJson = {
        "users": []
    }

    for user in users:
        usersJson["users"].append(
            {
                "user_id": user.user_id,
                "email": user.email,
            }
        )

    return json.dumps(usersJson)


@app.route('/test/fitbitusers', methods=["POST", "GET"])
def fitbitUsers():
    fitbitUsers = getAll(FitbitUsers)

    fitbitUsersJson = {
        "fitbit_users": []
    }

    for fitbitUser in fitbitUsers:
        fitbitUsersJson["fitbit_users"].append(
            {
                "fitbit_user_id": fitbitUser.fitbit_user_id,
                "user_id": fitbitUser.user_id,
                "access_token": fitbitUser.access_token
            }
        )

    return json.dumps(fitbitUsersJson)


@app.route('/test/usertokens')
def userTokens():
    tokens = getAll(UserAccessTokens)
    tokensJson = {
        "user_access_tokens": []
    }

    for token in tokens:
        tokensJson["user_access_tokens"].append(
            {
                "user_id": token.user_id,
                "access_token": token.access_token
            }
        )

    return json.dumps(tokensJson)


@app.route('/test/<userId>')
def test(userId):
    user = getByField(userId, Users.user_id, Users)

    return f'''
        <h1>{user.status_code}</h1>
        <h1>{user.message}</h1>
    '''


@app.route('/app/register', methods=['POST'])
def register():
    # Get email + password
    # Check if email exists
    # If true, return user_id = -1. If false, store email address + password
    # Get Users.user_id via email
    # Return user_id to flutter application
    req = request.json

    print(f"REQ IS ===== ${req}")

    email = req['email']
    password = req['password']

    # confirm that user does not exist
    response = getByField(email, Users.email, Users)

    print(f'STATUS CODE IS ${response.status_code}')

    # user does not exist in database
    if(response.status_code == 404):
        createUser(email, password)
        # get user record and get user id
        newResponse = findAndAuthenticateUser(email, password)

        print(f"NEW RESPONSE RESULT IS ===== ${newResponse.result.user_id}")

        jsonDict = {
            "user_id": newResponse.result.user_id,
            "status_code": newResponse.status_code,
            "message": "Successfully created user"
        }
        return json.dumps(jsonDict)
    else:
        jsonDict = [None]
        # user exists in database
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


@app.route('/app/login', methods=['POST'])
def login():
    req = request.authorization
    try:
        userId = request.form['user_id']
    except:
        userId = None

    class Resp:
        resp = ""

    print(f'REQ IS ====== {req}')

    if(userId is not None and userId >= 0):
        print(f"USER ID IS NOT NONE {userId}")
        Resp.resp = getByField(userId, Users.user_id, Users)
    else:
        print("USER ID IS NONE, GETTING VIA EMAIL AND PASSWORD")
        email = req['username']
        password = req['password']
        Resp.resp = findAndAuthenticateUser(email, password)

    # user exists
    if Resp.resp.status_code == 200:
        userAccessToken = updateUserToken(Resp.resp.result.user_id)

        jsonDict = {
            "access_token": userAccessToken,
            "status_code": Resp.resp.status_code,
            "user_id": Resp.resp.result.user_id,
            "message": Resp.resp.message,
            "base64_encoded": base64EncodeSecrets(Resp.resp.result.user_id, userAccessToken)
        }
        return json.dumps(jsonDict)

    print("USER NOT FOUND")

    jsonDict = {
        "status_code": Resp.resp.status_code,
        "user_id": -1,
        "message": Resp.resp.message,
    }

    return json.dumps(jsonDict)


@app.route('/fitbit/consent', methods=['POST'])
# Should only return url
def consent():
    # Receives base64 encoded Authorization: Basic userId:access_token
    try:
        req = request.authorization
        userId = req["username"]
        access_token = req["password"]
    except:
        return {
            "status_code": 400,
            "message": "Error: Bad request"
        }

    response = checkUserToken(userId, access_token)

    if(response.status_code != 200):
        jsonDict = {
            "status_code": response.status_code,
            "message": response.message,
        }
        json.dumps(jsonDict)

    # fitbitUser = getByField(userId, FitbitUsers.user_id, FitbitUsers)
    # if(fitbitUser['result'] is not None):
    #     # TODO: Check if token needs refresh
    #     return ""

    return f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={parsed_redirect_url}&scope={scope}&state={userId}"


@app.route('/fitbit/code', methods=['POST', 'GET'])
# Get Auth code from fitbit redirect url then exchange for access token
# Get user_id from consent
# Check if fitbit response fields are stored in the db, if not, add
# Should return HTML SUCCESS page
def code():
    print("Was able to get Authorization code!")
    # Get Auth code from url
    code = request.args.get('code')
    userId = request.args.get('state')

    print(f"PASSED STATE IS===={userId}\n")

    # Encode 'client_id:client_secret' to base64
    encoded_secret = base64EncodeSecrets(client_id, client_secret)

    # POST request for tokens
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
        raise Exception(fitbitUserJson)

    fitbitUserId = fitbitUserJson["user_id"]

    # get user & fitbitUser
    fitbitUser = getByField(
        fitbitUserId, FitbitUsers.fitbit_user_id, FitbitUsers
    )

    try:
        if(fitbitUser.result is None):
            print("Fitbit user doesn't exist, adding to db!")
            createFitbitUser(userId, fitbitUserJson)
        elif(
            fitbitUserJson['access_token'] != fitbitUser.result.access_token or
            fitbitUserJson['refresh_token'] != fitbitUser.result.refresh_token
        ):
            print("tokens are different, updating user!")
            updateFitbitUser(fitbitUserJson['user_id'], fitbitUserJson)

        date = "2020-08-08"

        accessToken = fitbitUserJson["access_token"]

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


@app.route('/fitbit/refresh')
# Refresh tokens
def refresh():
    userId = request.json['user_id']
    user = getFitbitUser(Mutable.userId)
    encoded_secret = base64EncodeSecrets(client_id, client_secret)
    req = requests.post(
        token_base_url,
        headers={
            'Authorization': f'Basic {encoded_secret}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }, params={
            'grant_type': 'refresh_token',
            'refresh_token': user.refresh_token,
            # expires_in defaults to 28800 or 8 hours
        }
    )

    userJson = req.json()

    # If an error is returned by fitbit api
    if(req.status_code != 200):
        raise Exception(f"{req.json()}{userJson}")

    updateFitbitUser(Mutable.userId, userJson)

    print("REFRESHED TOKEN! USER JSON IS ================ ", userJson)

    return


# Routes to fetch data from fitbit api


@app.route('/app/sleep', methods=['POST', 'GET'])
def getSleepRecords():
    req = request.authorization
    try:
        userId = req['username']
        accessToken = req['password']
    except:
        return "Headers are incorrect or missing"

    userToken = checkUserToken(userId, accessToken)

    if(userToken is None):
        return json.dumps(
            {
                "status_code": userToken.status_code,
                "message": userToken.message,
                "result": userToken.result
            }
        )

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


@app.route('/app/steps', methods=['POST', 'GET'])
def getStepsRecords():
    req = request.authorization
    try:
        userId = req['username']
        accessToken = req['password']
    except:
        return "Headers are incorrect or missing"

    userToken = checkUserToken(userId, accessToken)

    if(userToken is None):
        return json.dumps(
            {
                "status_code": userToken.status_code,
                "message": userToken.message,
                "result": userToken.result
            }
        )

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


@app.route('/app/calories', methods=['POST', 'GET'])
def getCaloriesRecords():
    req = request.authorization
    try:
        userId = req['username']
        accessToken = req['password']
    except:
        return "Headers are incorrect or missing"

    userToken = checkUserToken(userId, accessToken)

    if(userToken is None):
        return json.dumps(
            {
                "status_code": userToken.status_code,
                "message": userToken.message,
                "result": userToken.result
            }
        )

    caloriesRecords = getAllByField(userId, UserCalories, UserCalories.user_id)

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


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# http://192.168.100.6:5000/
