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

app = Flask(__name__)

client_id = "23B236"
client_secret = "07bdd4ade65de85abc9247e752cd49fc"
auth_base_url = "https://www.fitbit.com/oauth2/authorize"
token_base_url = "https://api.fitbit.com/oauth2/token"
flask_base_url = "http://127.0.0.1:5000"


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

    status = f"status:{req.status_code}"

    data = req.json()

    return f"""
    <h1>{status}</h1>
    <h1>{data}</h1>
    <h1></h1>
    """


if __name__ == "__main__":
    app.run()
