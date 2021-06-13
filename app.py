from flask import Flask

app = Flask(__name__)


@app.route('/',)
def getUser():
    return """
        <h1>HELLO WORDL</h1>
    """


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
