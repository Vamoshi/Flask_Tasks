# # sample link to fitbit user consent page, will return a code
# # https://www.fitbit.com/oauth2/authorize?
# # response_type=code&
# # client_id=23B27C&
# # redirect_uri=http://127.0.0.1:5000&
# # scope=activity%20nutrition%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight

# # sample redirect url:
# # 127.0.0.1:5000/?code=02f0201af31817b28aef2563479c1dfda69fd0cc#_=_
# # code is: 02f0201af31817b28aef2563479c1dfda69fd0cc

# # Flow
# # 1) go to consent page
# # 2) get code from redirect url
# # 3) exchange code for access + refresh token with a built url:
# # 4) POST https://api.fitbit.com/oauth2/token
# # 5) Add "Authorization" header with value "Basic Base64_encoded_string" where encoded_string = client_id:client_secret
# # 6) Add "Content-Type" header with value "application/x-www-form-urlencoded"
# # 7) Add "code" parameter with value of given code
# # 8) Add "grant_type" parameter with value of "authorization_code"
# # 9) Add "redirect" parameter with value of redirect url link
# # 10) Make request with the built url, Json object with access + refresh token will be returned
# # 11) Build second request with:
# # 12) GET https://api.fitbit.com/1/user/-/profile.json
# # 13) Add "Authorization" header with value of "Bearer access_token"
# # 14) Make request
# # 15) User Json Object will be returned

# # Useful links:
# # dev.fitbit.com/apps
# # dev.fitbit.com/build/reference/web-api/explore

# from flask import Flask, redirect, request
# from urllib import parse
# import requests
# import base64
# from db import *

# app = Flask(__name__)

# auth_base_url = "https://www.fitbit.com/oauth2/authorize"
# token_base_url = "https://api.fitbit.com/oauth2/token"
# flask_base_url = "http://127.0.0.1:5000"

# # client_id = "23B236"
# # client_secret = "07bdd4ade65de85abc9247e752cd49fc"
# client_id = "23B2TZ"
# client_secret = "a49b5d755ced923c7fd434a3a4c62383"


# class UserId:
#     value = ""


# # @app.route('/')
# # def index():
# #     # This route is for printing purposes
# #     redirect_url = parse.quote_plus(f"{flask_base_url}/code")
# #     secret_pair = f"{client_id}:{client_secret}"
# #     secret_bytes = secret_pair.encode("ascii")
# #     secret_base64_bytes = base64.b64encode(secret_bytes)
# #     encoded_secret = secret_base64_bytes.decode('ascii')

# #     return f"""<h1>Index {redirect_url} {client_id}</h1>
# #     <h1>{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
# #     <h1>https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=23B236&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Fcode&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800</h1>
# #     <h1>{encoded_secret}</h1>
# #     """

# # @app.route('/')
# # def index():


# @app.route('/consentpage')
# def consentPage():
#     # TODOS: CHECK IF ACCESS TOKEN EXISTS

#     # TODOS: CHECK IF ACCESS TOKEN IS ABOUT TO EXPIRE
#     # UPDATE REFRESH TOKEN IN DATABASE

#     redirect_url = parse.quote_plus(f"{flask_base_url}/code")
#     return redirect(f"{auth_base_url}?response_type=code&client_id={client_id}&redirect_uri={redirect_url}&scope=activity%20heartrate%20location%20nutrition%20profile%20settings%20sleep%20social%20weight&expires_in=604800")


# @app.route('/code')
# def code():
#     code = request.args.get('code')

#     redirect_url = f"{flask_base_url}/code"

#     secret_pair = f"{client_id}:{client_secret}"
#     secret_bytes = secret_pair.encode("ascii")
#     secret_base64_bytes = base64.b64encode(secret_bytes)
#     encoded_secret = secret_base64_bytes.decode('ascii')

#     req = requests.post(
#         token_base_url,
#         headers={
#             'Authorization': f'Basic {encoded_secret}',
#             'Content-Type': 'application/x-www-form-urlencoded'
#         }, params={
#             'code': code,
#             'grant_type': 'authorization_code',
#             'redirect_uri': redirect_url
#         }
#     )

#     # # get response status
#     # status = f"status:{req.status_code}"
#     # print(status)

#     # get response as json
#     data = req.json()

#     # cache userID
#     UserId.value = data["user_id"]

#     # get user
#     user = getUser(data["user_id"])

#     # if user doesn't exist, create new user
#     if(user == None):
#         print("IM INSIDE")
#         setUser(
#             data["user_id"],
#             data["access_token"],
#             data["expires_in"],
#             data["refresh_token"],
#             data["scope"]
#         )

#     return redirect('/access')


# @app.route('/access')
# def access():
#     result = ''
#     try:
#         result = getUser(UserId.value)
#     except:
#         result = None

#     return f"""
#     <h1>User = {UserId.value}</h1>
#     <h1>User is {result}</h1>
#     <h1></h1>
#     """


# if __name__ == "__main__":
#     app.run()
