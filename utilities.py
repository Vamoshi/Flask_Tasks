# Modules
import base64
from datetime import datetime

# User defined modules
from repository import getFitbitUser


def base64EncodeSecrets(id, secret):
    secretPair = f"{id}:{secret}"
    secretBytes = secretPair.encode("ascii")
    secretBase64Bytes = base64.b64encode(secretBytes)
    encodedSecret = secretBase64Bytes.decode('ascii')
    return encodedSecret


def tokenNeedRefresh(fitbitUser):
    today = datetime.now()
    secondsElapsed = ((today - fitbitUser.time_fetched).total_seconds())

    # 30 minutes
    seconds = 1800

    # Check if the access token is available for only 30 minutes more
    return secondsElapsed > (fitbitUser.expires_in - seconds) and secondsElapsed > 120
