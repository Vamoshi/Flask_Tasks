# Modules
from re import L
from flask import Flask, redirect, request, url_for
from urllib import parse
import requests

# User defined modules
from database import engine
from repository import addUser, authenticateUser, createUser, getUser, updateUser
import models
from utilities import base64EncodeSecrets, tokenNeedRefresh


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

# http://127.0.0.1:5000
#

# # # Fitbit Application Secrets:
# # Practice 2
# client_id = "23B236"
# client_secret = "07bdd4ade65de85abc9247e752cd49fc"
# # Practice 3
# client_id = "23B2TZ"
# client_secret = "a49b5d755ced923c7fd434a3a4c62383"
# # Practice 4
# client_id = "23B2GM"
# client_secret = "3dde7c4c650d7af98c0652fefef9815e"
# # login practice
client_id = "23B87P"
client_secret = "f770f00f4059332a9c8add74dadd7dcf"


class Mutable:
    # For debugging/development
    userId = ""
    fitbitUserId = ""
    route = ""
    accessToken = ""


# initiate database engine
models.Base.metadata.create_all(bind=engine)


# @app.route('/test/<route>')
# def test(route):
#     return redirect(f'/working/{route}')


@app.route('/fitbit/working')
def something():
    return '<h1>ITS WORKING!!</h1>'


# @app.route('/')
# # This route is for printing purposes
# def index():
#     # Encode 'client_id:client_secret' to base64
#     encoded_secret = base64EncodeSecrets(client_id, client_secret)

#     elapsed_time = tokenNeedRefresh(Mutable.userId)

#     return f"""<h1>Index {parsed_redirect_url} {client_id}</h1>
#     <h1>{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={parsed_redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
#     <h1>
#         https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B27C&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Ffitbit%2Fcode&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
#     </h1>
#     <h1>{encoded_secret}</h1>
#     <h1>Elapsed time: {elapsed_time}</h1>
#     """

@app.route('/')
def index():
    return f'''
        <h1>I am in index</h1>
    '''


@app.route('/app/register')
def register():
    # Get email + password
    # Check if email exists
    # If true, return error. If false, store email address + password
    # Get email address
    email = request.args.get('email')
    password = request.args.get('password')

    createUser(email, password)

    return f'''
        <h1>{email}</h1>
        <h1>{password}</h1>
        <h1></h1>
    '''


@app.route('/app/login')
def login():
    email = request.args.get('email')
    password = request.args.get('password')

    response = authenticateUser(email, password)

    if(response.result is not None):
        user = response.result
        return f'''
            <h1>{response.status}</h1>
            <h1>{user.email}</h1>
            <h1>{user.password}</h1>
            <h1>{response.message}</h1>
            <h1></h1>
        '''

    return f'''
        <h1>{response.status}</h1>
        <h1>{response.result}</h1>
        <h1>{response.message}</h1>
        <h1></h1>
    '''


# @app.route('/fitbit/crossroad/<route>')
# # This is the only endpoint accessible by flutter
# # ASK HOW TO PASS VARIABLES VIA THIS ROUTE!!
# def crossroad(route):
#     # Store route
#     Mutable.route = route

#     # If Mutable.userId is null, get it,
#     if(Mutable.userId == ""):
#         print("Mutable.userId is null")
#         return redirect('/fitbit/consent')
#     # If User doesn't exist in database, create it
#     elif(getUser(Mutable.userId) == None):
#         print("User is not in database")
#         return redirect('/fitbit/consent')
#     # If only 30 minutes are left til access token expires, and more than 2 minutes have passed, refresh it
#     elif(tokenNeedRefresh(Mutable.userId)):
#         print("Need to refresh user tokens")
#         return redirect('/fitbit/refresh')

#     print("Mutable.userId is not null \n User is in database \n No need to refresh token")
#     # Go to the route passed by flutter
#     return redirect(f"/fitbit/{Mutable.route}")


@app.route('/fitbit/consent')
def consent():
    return redirect(f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800")


@app.route('/fitbit/code')
# Get Auth code from fitbit redirect url then exchange for access token
# Get user_id in fitbit response then store in Mutable.userId
# Check if fitbit response fields are stored in the db, if not, add
def code():
    print("Was able to get Authorization code!")
    # Get Auth code from url
    code = request.args.get('code')

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
            'redirect_uri': redirect_url
        }
    )

    # # get response status
    # status = f"status:{req.status_code}"
    # print(status)

    # get response as json
    userJson = req.json()

    print(f"USERJSON IS ============== {userJson}")

    # If an error is returned by fitbit api
    if(req.status_code != 200):
        raise Exception(userJson)

    # cache userID
    Mutable.userId = userJson["user_id"]

    # cache access token
    Mutable.accessToken = userJson["access_token"]

    # # get user
    # user = getUser(userJson["user_id"])

    # # if user is None, create new user record in db
    # if(user == None):
    #     print("User doesn't exist, adding user to db")
    #     addUser(userJson)
    # # Check tokens stored in db with the newly fetched token, if different, update
    # elif(userJson["access_token"] != user.access_token or userJson["refresh_token"] != user.refresh_token):
    #     print("Tokens are different, updating user")
    #     updateUser(Mutable.userId, userJson)

    # # return redirect('/fitbit/access')
    # return redirect(f'/fitbit/{Mutable.route}')

    return redirect('/fitbit/steps/2020-09-01')


@app.route('/fitbit/access')
def access():
    result = getUser(Mutable.userId)

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
    # user = getUser(Mutable.userId)
    req = requests.get(
        f"{fitbit_api_url}/{user_1_url}/profile.json",
        headers={
            'Authorization': f'Bearer {Mutable.accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    profileJson = req.json()
    profile = profileJson["user"]

    return profile


@app.route('/fitbit/sleep/<date>')
def getFitbitSleep(date):
    # date format is YYYY-MM-DD
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/sleep/date/{date}.json",
        headers={
            'Authorization': f'Bearer {Mutable.accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    sleepJson = req.json()

    return sleepJson["summary"]


@app.route('/fitbit/steps/<date>')
def getFitbitSteps(date):
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {Mutable.accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    stepsJson = req.json()
    steps = stepsJson["summary"]["steps"]

    return stepsJson["summary"]


@app.route('/fitbit/calories/<date>')
def getFitbitCalories(date):
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {Mutable.accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    caloriesJson = req.json()
    calories = caloriesJson["calories"]

    return caloriesJson["summary"]


@app.route('/fitbit/refresh')
# Refresh tokens
def refresh():
    user = getUser(Mutable.userId)
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

    updateUser(Mutable.userId, userJson)

    print("REFRESHED TOKEN! USER JSON IS ================ ", userJson)

    # return redirect(f'/fitbit/access')
    return redirect(f'/fitbit/{Mutable.route}')


if __name__ == "__main__":
    app.run()
