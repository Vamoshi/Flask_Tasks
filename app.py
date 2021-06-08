# Modules
from flask import Flask, redirect, request
from urllib import parse
import requests
import base64

# User defined modules
from database import engine, SessionLocal, addUser, getUser, updateUser
import models


app = Flask(__name__)

# URLS
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"
redirect_url = f"{flask_base_url}/fitbit/code"
parsed_redirect_url = parse.quote_plus(redirect_url)

# # SECRETS
# client_id = "23B236"
# client_secret = "07bdd4ade65de85abc9247e752cd49fc"
# client_id = "23B2TZ"
# client_secret = "a49b5d755ced923c7fd434a3a4c62383"
client_id = "23B27C"
client_secret = "8b872cb6e9f765aaf5d18501e5595b60"


class Mutable:
    # Store mutable variables here
    userId = ""


# initiate database engine
models.Base.metadata.create_all(bind=engine)


@app.route('/')
# This route is for printing purposes
def index():
    # Encode 'client_id:client_secret' to base64
    secret_pair = f"{client_id}:{client_secret}"
    secret_bytes = secret_pair.encode("ascii")
    secret_base64_bytes = base64.b64encode(secret_bytes)
    encoded_secret = secret_base64_bytes.decode('ascii')

    return f"""<h1>Index {parsed_redirect_url} {client_id}</h1>
    <h1>{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={parsed_redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
    <h1>
        https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B27C&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Ffitbit%2Fcode&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800
    </h1>
    <h1>{encoded_secret}</h1>
    """


@app.route('/fitbit/init')
# Do startup checks
def init():
    # CHECK IF User.value != ""
    # IF TRUE, GET USERID VIA CONSENTPAGE

    # IF FALSE CHECK IF ACCESS TOKEN + USER EXISTS
    # IF FALSE, ROUTE TO CONSENT PAGE

    # CHECK IF ACCESS TOKEN IS ABOUT TO EXPIRE
    # IF TRUE ROUTE TO REFRESH TOKEN THEN STORE NEW TOKENS IN DATABASE
    # IF FALSE, JUST SET USER.VALUE TO USERID
    pass


@app.route('/fitbit/refresh')
# Refresh tokens
def refresh():
    pass


@app.route('/fitbit/consent')
def consentPage():
    return redirect(f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800")


@app.route('/fitbit/code')
# Get Auth code from fitbit redirect url then exchange for access token
# Get user_id in fitbit response then store in User.value
# Check if fitbit response fields are stored in the db, if not, add
def code():
    # Get Auth code from url
    code = request.args.get('code')

    # Encode 'client_id:client_secret' to base64
    secret_pair = f"{client_id}:{client_secret}"
    secret_bytes = secret_pair.encode("ascii")
    secret_base64_bytes = base64.b64encode(secret_bytes)
    encoded_secret = secret_base64_bytes.decode('ascii')

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

    print("USER JSON IS ================ ", userJson)

    try:
        # cache userID
        Mutable.userId = userJson["user_id"]
    except:
        # Error was thrown by fitbit
        raise Exception(userJson)

    # get user from database
    session = SessionLocal()
    user = getUser(session, userJson["user_id"])
    session.close()

    # if user is None, create new user record in db
    if(user == None):
        print("User doesn't exist, adding user to db")

        try:
            session = SessionLocal()
            addUser(session, userJson)
            session.commit()
        except:
            session.rollback()
            raise Exception("Couldn't add user to database")
        finally:
            session.close()

    return redirect('/fitbit/access')


@app.route('/fitbit/access')
def access():
    session = SessionLocal()
    result = getUser(session, Mutable.userId)
    session.close()

    return f"""
    <h1>User = {Mutable.userId}</h1>
    <h1>User is {result.time_fetched}</h1>
    <h1></h1>
    """


if __name__ == "__main__":
    app.run()
