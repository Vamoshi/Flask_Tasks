from flask import Flask, redirect, url_for, request
import requests

app = Flask(__name__)

if __name__ == "__main__":
    app.run()


@app.route('/api/user',)
def getUser():
    userId = request.args.get('userId', None)
    r = requests.get(f"https://api.github.com/user/{userId}")
    return r.json()


@app.route('/api/repositories')
def getRepositories():
    searchString = request.args.get('searchString', None)
    page = request.args.get('page', None)
    r = requests.get(
        f"https://api.github.com/search/repositories?q=${searchString}&sort=stars&order=desc&per_page=20&page=${page}")
    return r.json()

# https://api.github.com/search/repositories?q=$searchString&sort=stars&order=desc&per_page=20&page=$page
