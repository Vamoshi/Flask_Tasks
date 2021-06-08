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

# json to User
# data["user_id"],
# data["access_token"],
# data["expires_in"],
# data["refresh_token"],
# data["scope"]
