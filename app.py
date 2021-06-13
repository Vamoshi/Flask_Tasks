from flask import Flask, redirect, url_for, request
import requests

app = Flask(__name__)

if __name__ == "__main__":
    app.run()


@app.route('/',)
def getUser():
    return """
        <h1>HELLO WORDL</h1>
    """
