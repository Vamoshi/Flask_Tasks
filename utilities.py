# Modules
import base64
from datetime import datetime

# User defined modules
from repository import getUser


def base64EncodeSecrets(clientId, clientSecret):
    secretPair = f"{clientId}:{clientSecret}"
    secretBytes = secretPair.encode("ascii")
    secretBase64Bytes = base64.b64encode(secretBytes)
    encodedSecret = secretBase64Bytes.decode('ascii')
    return encodedSecret


def tokenNeedRefresh(userId):
    user = getUser(userId)
    today = datetime.now()
    secondsElapsed = ((today - user.time_fetched).total_seconds())

    # 30 minutes
    seconds = 1800

    # Check if the access token is available for only 30 minutes more
    return secondsElapsed > (user.expires_in - seconds) and secondsElapsed > 120
