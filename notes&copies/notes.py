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
# dev.fitbit.com/build/reference/web-api/explore/

# json to User
# data["user_id"],
# data["access_token"],
# data["expires_in"],
# data["refresh_token"],
# data["scope"]

# req = request.authorization
# try:
#     userId = req['username']
#     accessToken = req['password']
# except:
#     return "Headers are incorrect or missing"

# userToken = checkUserToken(userId, accessToken)

# if(userToken is None):
#     return json.dumps(
#         {
#             "status_code": userToken.status_code,
#             "message": userToken.message,
#             "result": userToken.result
#         }
#     )


# @auth.login_required
# @app.route('/v1/users', methods=['POST'])
# def users():
#     # If email and password are passed in json body, it means it's a registration
#     fromUser = request.json

#     try:
#         email = fromUser['email']
#         password = fromUser['password']
#     except:
#         email = None
#         password = None

#     if(email is not None and password is not None):
#         # register
#         # confirm that user does not exist
#         response = getByField(email, Users.email, Users)
#         # user does not exist in database
#         if(response.status_code == 404):
#             record = Users(
#                 email=email,
#                 password=password
#             )
#             addDatabaseRecord(record)
#             # get user record and get user id
#             newResponse = findAndAuthenticateUser(email, password)

#             jsonDict = {
#                 "user_id": newResponse.result.user_id,
#                 "status_code": newResponse.status_code,
#                 "message": "Successfully created user"
#             }
#             return json.dumps(jsonDict)
#         else:
#             jsonDict = [None]
#             # user exists in database
#             if(response.status_code == 200):
#                 jsonDict[0] = {
#                     "status_code": response.status_code,
#                     "user_id": -1,
#                     "message": "User already exists"
#                 }
#             # Something went wrong in database
#             else:
#                 jsonDict[0] = {
#                     "status_code": response.status_code,
#                     "user_id": -1,
#                     "message": response.message
#                 }

#             return json.dumps(jsonDict[0])
#     # login then return token to user
#     elif(auth.current_user() is not None):
#         # generate a token
#         return