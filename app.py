from flask import Flask, redirect, request
from urllib import parse
import requests
import base64
from database import engine, addUser, getUser, updateUser, SessionLocal
import models


app = Flask(__name__)

# URLS
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"

# SECRETS
# client_id = "23B236"
# client_secret = "07bdd4ade65de85abc9247e752cd49fc"
client_id = "23B2TZ"
client_secret = "a49b5d755ced923c7fd434a3a4c62383"


class UserId:
    value = ""


models.Base.metadata.create_all(bind=engine)


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

@app.route('/fitbit/init')
def init():
    # CHECK IF User.value != ""
    # IF TRUE, GET USERID VIA CONSENTPAGE

    # IF FALSE CHECK IF ACCESS TOKEN + USER EXISTS
    # IF FALSE, ROUTE TO CONSENT PAGE

    # CHECK IF ACCESS TOKEN IS ABOUT TO EXPIRE
    # IF TRUE ROUTE TO REFRESH TOKEN THEN STORE NEW TOKENS IN DATABASE
    # IF FALSE, JUST SET USER.VALUE TO USERID
    pass


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
        print("IM INSIDE")
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
