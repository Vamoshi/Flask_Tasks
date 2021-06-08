# Modules
from flask import Flask, redirect, request, url_for
from urllib import parse
import requests

# User defined modules
from database import engine
from repository import addUser, getUser, updateUser
import models
from utilities import base64EncodeSecrets, tokenNeedRefresh


app = Flask(__name__)

# URLS
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"
redirect_url = f"{flask_base_url}/fitbit/code"
parsed_redirect_url = parse.quote_plus(redirect_url)

# # # Fitbit Application Secrets:
# # Practice 2
# client_id = "23B236"
# client_secret = "07bdd4ade65de85abc9247e752cd49fc"
# # Practice 3
# client_id = "23B2TZ"
# client_secret = "a49b5d755ced923c7fd434a3a4c62383"
# # Practice 4
client_id = "23B2SS"
client_secret = "14c64f9b219e1092e6ac0477f7cd0c69"
# # login practice
# client_id = "23B27C"
# client_secret = "8b872cb6e9f765aaf5d18501e5595b60"


class Mutable:
    # Store mutable variables here
    userId = ""
    route = ""


# initiate database engine
models.Base.metadata.create_all(bind=engine)


# @app.route('/test/<route>')
# def test(route):
#     return redirect(f'/working/{route}')


@app.route('/fitbit/working')
def something():
    return '<h1>ITS WORKING!!</h1>'


@app.route('/')
# This route is for printing purposes
def index():
    # Encode 'client_id:client_secret' to base64
    encoded_secret = base64EncodeSecrets(client_id, client_secret)

    elapsed_time = tokenNeedRefresh(Mutable.userId)

    return f"""<h1>Index {parsed_redirect_url} {client_id}</h1>
    <h1>{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={parsed_redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
    <h1>
        https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B27C&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Ffitbit%2Fcode&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
    </h1>
    <h1>{encoded_secret}</h1>
    <h1>Elapsed time: {elapsed_time}</h1>
    """


@app.route('/fitbit/crossroad/<route>')
# This is the only endpoint accessible by flutter
#
def crossroad(route):
    # Store route
    Mutable.route = route

    # If Mutable.userId is null, get it,
    if(Mutable.userId == ""):
        print("Mutable.userId is null")
        return redirect('/fitbit/consent')
    # If User doesn't exist in database, create it
    elif(getUser(Mutable.userId) == None):
        print("User is not in database")
        return redirect('/fitbit/consent')
    # If only 30 minutes are left til access token expires, and more than 2 minutes have passed, refresh it
    elif(tokenNeedRefresh(Mutable.userId)):
        print("Need to refresh user tokens")
        return redirect('/fitbit/refresh')

    print("Mutable.userId is not null \n User is in database \n No need to refresh token")
    # Go to the route passed by flutter
    return redirect(f"/fitbit/{Mutable.route}")


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

    return redirect(f'/fitbit/access')
    # return redirect(f'/fitbit/{Mutable.route}')


@app.route('/fitbit/consent')
def consent():
    return redirect(f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800")


@app.route('/fitbit/code')
# Get Auth code from fitbit redirect url then exchange for access token
# Get user_id in fitbit response then store in Mutable.userId
# Check if fitbit response fields are stored in the db, if not, add
def code():
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

    # get user
    user = getUser(userJson["user_id"])

    # if user is None, create new user record in db
    if(user == None):
        print("User doesn't exist, adding user to db")
        addUser(userJson)
    # Check tokens stored in db with the newly fetched token, if different, update
    elif(userJson["access_token"] != user.access_token or userJson["refresh_token"] != user.refresh_token):
        print("Tokens are different, updating user")
        updateUser(Mutable.userId, userJson)

    return redirect('/fitbit/access')
    # return redirect(f'/fitbit/{Mutable.route}')


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


if __name__ == "__main__":
    app.run()
