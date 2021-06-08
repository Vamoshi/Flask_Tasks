from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(6), nullable=False)
    access_token = db.Column(db.Text)
    expires_in = db.Column(db.Integer)
    refresh_token = db.Column(db.Text)
    scope = db.Column(db.Text)
    time_fetched = db.Column(db.DateTime)


db.create_all()


# def __initiate():
#     connection = sqlite3.connect('user.db')
#     cursor = connection.cursor()

#     return connection, cursor


# def __close(connection, cursor):
#     cursor.close()
#     connection.close()


# def __createTable():
#     connection, cursor = __initiate()

#     # Add datetime field
#     query = """
#             CREATE TABLE IF NOT EXISTS
#             user_table(
#                 user_id TEXT PRIMARY KEY,
#                 access_token TEXT,
#                 expires_in INTEGER,
#                 refresh_token TEXT,
#                 scope TEXT
#             )
#             """

#     cursor.execute(query)

#     __close(connection, cursor)


def setUser(userId, accessToken, expiresIn, refreshToken, scope):
    print("SETTING  USER!!!")
    print(f"USER ID IS {userId}------------------------")
    print(type(userId))
    user = User(
        user_id=userId,
        access_token=accessToken,
        expires_in=expiresIn,
        refresh_token=refreshToken,
        scope=scope
    )

    db.session.add(user)
    db.session.commit()

    # __createTable()
    # connection, cursor = __initiate()

    # timeFetched = ''

    # query = """
    #     INSERT INTO
    #         user_table(
    #             user_id,
    #             access_token,
    #             expires_in,
    #             refresh_token,
    #             scope
    #         )
    #     VALUES
    #         (?,?,?,?,?);
    # """

    # data_tuple = (userId, accessToken, expiresIn, refreshToken, scope)

    # cursor.execute(query, data_tuple)
    # connection.commit()

    # __close(connection, cursor)


def getUser(userId):
    print("GETTING  USER!!!")

    try:
        return User.query.filter_by(user_id=userId).first()
    except:
        return None

    # __createTable()
    # connection, cursor = __initiate()

    # try:
    #     query = f"""
    #         SELECT * FROM user_table WHERE user_id=?;
    #     """
    #     cursor.execute(query, [userId])

    # except:
    #     print("error fetching user")
    #     return None

    # result = cursor.fetchone()

    # __close(connection, cursor)
    # return result
