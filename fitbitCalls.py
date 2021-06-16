from datetime import datetime
from models import UserCalories, UserSleep, UserSteps
from repository import addRecord
import requests


def addFitbitSleep(userId, accessToken, fitbit_api_url, user_1_2_url, date):
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/sleep/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    sleepJson = req.json()

    addRecord(
        UserSleep(
            user_id=userId,
            total_minutes_asleep=sleepJson['summary']['totalMinutesAsleep'],
            total_time_in_bed=sleepJson['summary']['totalTimeInBed'],
            date=datetime.strptime(date, '%Y-%m-%d')
        )
    )


def addFitbitSteps(userId, accessToken, fitbit_api_url, user_1_2_url, date):
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    stepsJson = req.json()
    steps = stepsJson["summary"]["steps"]

    addRecord(
        UserSteps(
            user_id=userId,
            steps=steps,
            date=datetime.strptime(date, '%Y-%m-%d')
        )
    )


def addFitbitCalories(userId, accessToken, fitbit_api_url, user_1_2_url, date):
    req = requests.get(
        f"{fitbit_api_url}/{user_1_2_url}/activities/date/{date}.json",
        headers={
            'Authorization': f'Bearer {accessToken}'
        }
    )

    if(req.status_code != 200):
        raise Exception(f"Error: {req.json()}")

    caloriesJson = req.json()
    caloriesSummary = caloriesJson["summary"]
    calories = caloriesSummary['calories']

    addRecord(
        UserCalories(
            user_id=userId,
            bmr=calories['bmr'],
            calories_total=calories['total']
        )
    )
