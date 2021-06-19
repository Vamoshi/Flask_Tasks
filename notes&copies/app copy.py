# sample link to fitbit user consent page, will return a code
# https://www.fitbit.com/oauth2/authorize?
# response_type=code&
# client_id=23B27C&
# redirect_uri=http://127.0.0.1:5000&
# scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight

# sample redirect url:
# 127.0.0.1:5000/?code=02f0201af31817b28aef2563479c1dfda69fd0cc#_=_
# code is: 02f0201af31817b28aef2563479c1dfda69fd0cc

# Flow
# 1) go to consent page
# 2) get code from redirect url
# 3) exchange code for access + refresh token with a built url:
# 4) POST https://api.fitbit.com/oauth2/token
# 5) Add "Authorization" header with value "Basic Base64_encoded_string" where encoded_string = client_id:client_secret
# 6) Add "Content-Type" header with value "application/x-www-form-urlencoded"
# 7) Add "code" parameter with value of given code
# 8) Add "grant_type" parameter with value of "authorization_code"
# 9) Add "redirect" parameter with value of redirect url link
# 10) Make request with the built url, Json object with access + refresh token will be returned
# 11) Build second request with:
# 12) GET https://api.fitbit.com/1/user/-/profile.json
# 13) Add "Authorization" header with value of "Bearer access_token"
# 14) Make request
# 15) User Json Object will be returned

# Useful links:
# dev.fitbit.com/apps
# dev.fitbit.com/build/reference/web-api/explore

from flask import Flask, redirect, request
from urllib import parse
import requests
import base64
from db import setUser, getUser

app = Flask(__name__)


auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"

# client_id = "23B236"
# client_secret = "07bdd4ade65de85abc9247e752cd49fc"
client_id = "23B2TZ"
client_secret = "a49b5d755ced923c7fd434a3a4c62383"


class UserId:
    value = ""


@app.route('/')
def index():
    # This route is for printing purposes
    redirect_url = parse.quote_plus(f"{flask_base_url}/code")
    secret_pair = f"{client_id}:{client_secret}"
    secret_bytes = secret_pair.encode("ascii")
    secret_base64_bytes = base64.b64encode(secret_bytes)
    encoded_secret = secret_base64_bytes.decode('ascii')

    return f"""<h1>Index {redirect_url} {client_id}</h1>
    <h1>{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
    <h1>https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B236&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcode&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
    <h1>{encoded_secret}</h1>
    """


# @app.route('/')
# def index():


@ app.route('/v1/registration', methods=['POST'])
def registration():
    # retrieve email + password
    fromUser = request.json

    email = fromUser['email']
    password = fromUser['password']

    # confirm that user does not exist
    response = getByField(email, Users.email, Users)

    # user does not exist in database
    if(response.status_code == 404):
        record = Users(
            email=email,
            password=password
        )
        addDatabaseRecord(record)
        # get user record and get user id
        newResponse = findAndAuthenticateUser(email, password)

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


@ app.route('/v1/login', methods=['POST'])
def login():
    # get username + password
    fromUser = request.authorization

    # check if user_id was passed
    try:
        userId = request.form['user_id']
    except:
        userId = None

    # Tried to use nonlocal keyword, but it doesn't work, so created mutable class
    class Query:
        user = ""

    if(userId is not None and userId >= 0):
        print(f"USER ID IS NOT NONE {userId}")
        Query.user = getByField(userId, Users.user_id, Users)
    else:
        print("USER ID IS NONE, GETTING VIA EMAIL AND PASSWORD")
        email = fromUser['username']
        password = fromUser['password']
        Query.user = findAndAuthenticateUser(email, password)

    # user exists
    if Query.user.status_code == 200:
        # Update user token
        userAccessToken = updateUserToken(Query.user.result.user_id)

        jsonDict = {
            "access_token": userAccessToken,
            "status_code": Query.user.status_code,
            "user_id": Query.user.result.user_id,
            "message": Query.user.message,
        }
        return json.dumps(jsonDict)

    # user doesn't exist
    jsonDict = {
        "status_code": Query.user.status_code,
        "user_id": -1,
        "message": Query.user.message,
    }

    return json.dumps(jsonDict)


@app.route('/consentpage')
def consentPage():
    redirect_url = parse.quote_plus(f"{flask_base_url}/code")
    return redirect(f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800")


@app.route('/code')
def code():
    code = request.args.get('code')

    redirect_url = f"{flask_base_url}/code"

    secret_pair = f"{client_id}:{client_secret}"
    secret_bytes = secret_pair.encode("ascii")
    secret_base64_bytes = base64.b64encode(secret_bytes)
    encoded_secret = secret_base64_bytes.decode('ascii')

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
    data = req.json()

    # cache userID
    UserId.value = data["user_id"]

    # get user
    user = getUser(data["user_id"])

    # if user doesn't exist, create new user
    if(user == None):
        setUser(
            data["user_id"],
            data["access_token"],
            data["expires_in"],
            data["refresh_token"],
            data["scope"]
        )

    return redirect('/access')


@app.route('/access')
def access():
    result = getUser(UserId.value)

    return f"""
    <h1>User = {UserId.value}</h1>
    <h1>User is {result}</h1>
    <h1></h1>
    """


if __name__ == "__main__":
    app.run()
