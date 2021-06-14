# Modules
from datetime import datetime
from flask import Flask, redirect, request, url_for
from urllib import parse
import requests
from werkzeug.wrappers import response

# User defined modules
from database import engine
from repository import addRecord, createFitbitUser, findAndAuthenticateUser, createUser, getAll, getByField, getFitbitUser, getUserAccessToken, updateFitbitUser
from utilities import base64EncodeSecrets, tokenNeedRefresh
from models import FitbitUsers, UserCalories, UserSleep, UserSteps, Users
import models
import json

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
client_id = "23B8TC"
client_secret = "7f470c673a92fa6eaf366b8d5f7ffcfc"


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


# @app.route('/test/<route>')
# def test(route):
#     return redirect(f'/working/{route}')

@app.route('/')
def index():
    return "<h1>THIS IS THE INDEX</h1>"


@app.route('/test/users', methods=["POST", "GET"])
def users():
    users = getAll(Users)
    print(users)

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
    print(fitbitUsers)

    fitbitUsersJson = {
        "fitbitUsers": []
    }

    for fitbitUser in fitbitUsers:
        fitbitUsersJson["fitbitUsers"].append(
            {
                "fitbit_user_id": fitbitUser.fitbit_user_id,
                "user_id": fitbitUser.user_id,
                "access_token": fitbitUser.access_token
            }
        )

    return json.dumps(fitbitUsersJson)


@app.route('/fitbit/working')
def something():
    return '<h1>ITS WORKING!!</h1>'


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
    req = request.json
    userId = req['user_id']

    # ask how to convert to nonlocal
    class Resp:
        resp = ""

    if(userId is not None and userId >= 0):
        print(f"USER ID IS NOT NONE {userId}")
        Resp.resp = getByField(userId, Users.user_id, Users)
        # TODO: check if user has a registered fitbit account
        # if not, prompt user in flutter which would lead to consent page
        # if yes, get access token then check if it has expired
        # refresh if expired
        # fitbitUserResp = getByField(userId, FitbitUsers.user_id, FitbitUsers)
        # fitbitUser = fitbitUserResp.result
        # if(fitbitUser is not None):
        #     return redirect('/fitbit/refresh')
    else:
        print("USER ID IS NONE, GETTING VIA EMAIL AND PASSWORD")
        email = req['email']
        password = req['password']
        Resp.resp = findAndAuthenticateUser(email, password)

    # user exists
    if Resp.resp.status_code == 200:

        jsonDict = {
            "status_code": Resp.resp.status_code,
            "user_id": Resp.resp.result.user_id,
            "message": Resp.resp.message
        }
        return json.dumps(jsonDict)

    print("USER NOT FOUND")

    jsonDict = {
        "status_code": Resp.resp.status_code,
        "user_id": -1,
        "message": Resp.resp.message
    }

    return json.dumps(jsonDict)


@app.route('/fitbit/consent', methods=['POST'])
# Should only return url
def consent():
    # get userId from application via POST
    req = request.json
    userId = req['user_id']

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

    print(f"FITBITUSERJSON IS ============== {fitbitUserJson}")

    # If an error is returned by fitbit api
    if(req.status_code != 200):
        raise Exception(fitbitUserJson)

    fitbitUserId = fitbitUserJson["user_id"]

    # get user & fitbitUser
    fitbitUser = getByField(
        fitbitUserId, FitbitUsers.fitbit_user_id, FitbitUsers
    )

    if(fitbitUser.result is None):
        print("Fitbit user doesn't exist, adding to db!")
        createFitbitUser(userId, fitbitUserJson)

        return """
            <div style="min-height: 100vh; display: grid; place-items: center;">
                <h1>SUCCESSFULLY LOGGED IN TO FITBIT! <br/>
                    YOU MAY NOW CLOSE THIS WINDOW!
                </h1>
            </div>
            """
    elif(
        fitbitUserJson['access_token'] != fitbitUser.result.access_token or
        fitbitUserJson['refresh_token'] != fitbitUser.result.refresh_token
    ):
        print("tokens are different, updating user!")
        updateFitbitUser(fitbitUserJson['user_id'], fitbitUserJson)
        return """
            <div style="min-height: 100vh; display: grid; place-items: center;">
                <h1>SUCCESSFULLY LOGGED IN TO FITBIT! <br/>
                    YOU MAY NOW CLOSE THIS WINDOW!
                </h1>
            </div>
            """

    return """
    <div style="min-height: 100vh; display: grid; place-items: center;">
        <h1>SOMETHING WENT WRONG! <br/>
            YOU MAY NOW CLOSE THIS WINDOW!
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


@app.route('/fitbit/access')
def access():
    result = getFitbitUser(Mutable.userId)

    return f"""
        <h1>User = {Mutable.userId}</h1>
        <h1>Access Token: {result.access_token}</h1>
        <h1>Refresh Token: {result.refresh_token}</h1>
        <h1>Access Token requested on {result.time_fetched}</h1>
        <h1></h1>
    """

# Routes to fetch data from fitbit api


@app.route('/fitbit/profile')
def profile():
    received = request.json
    userId = received['user_id']
    accessToken = getUserAccessToken(userId)

    # user = getUser(Mutable.userId)
    req = requests.get(
        f"{fitbit_api_url}/{user_1_url}/profile.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    profileJson = req.json()
    profile = profileJson["user"]

    return profile


@app.route('/fitbit/sleep/<date>', methods=['POST', 'GET'])
def getFitbitSleep(date):
    # date format is YYYY-MM-DD
    received = request.json
    userId = received['user_id']
    accessToken = getUserAccessToken(userId)

    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/sleep/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    sleepJson = req.json()

    addRecord(
        UserSleep(
            user_id=userId,
            total_minutes_asleep=sleepJson['summary']['totalMinutesAsleep'],
            total_time_in_bed=sleepJson['summary']['totalTimeInBed'],
            date=datetime.strptime(date, '%Y-%m-%d')
        )
    )

    jsonDict = {
        "totalMinutesAsleep": sleepJson['summary']['totalMinutesAsleep'],
        "totalTimeInBed": sleepJson['summary']['totalTimeInBed'],
        'date': date
    }

    return json.dumps(jsonDict)


@app.route('/fitbit/steps/<date>', methods=['POST', 'GET'])
def getFitbitSteps(date):
    received = request.json
    userId = received['user_id']
    accessToken = getUserAccessToken(userId)

    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    stepsJson = req.json()
    steps = stepsJson["summary"]["steps"]

    addRecord(
        UserSteps(
            user_id=userId,
            steps=steps,
            date=datetime.strptime(date, '%Y-%m-%d')
        )
    )

    jsonDict = {
        'steps': steps,
        'date': date
    }

    return json.dumps(jsonDict)


@app.route('/fitbit/calories/<date>', methods=['POST', 'GET'])
def getFitbitCalories(date):
    received = request.json
    userId = received['user_id']
    accessToken = getUserAccessToken(userId)

    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    caloriesJson = req.json()
    caloriesSummary = caloriesJson["summary"]
    calories = caloriesSummary['calories']

    print(f"CALORIES JSON IS ======== {caloriesJson}")
    print(f"CALORIES IS {calories}")
    addRecord(
        UserCalories(
            user_id=userId,
            bmr=calories['bmr'],
            calories_total=calories['total']
        )
    )

    return calories


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

# http://192.168.100.6:5000/
