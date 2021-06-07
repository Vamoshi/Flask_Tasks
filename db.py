from os import error
import sqlite3


def _createTable():
    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    # Add datetime field
    query = """
            CREATE TABLE IF NOT EXISTS
            user_table(
                user_id TEXT PRIMARY KEY, 
                access_token TEXT,
                expires_in INTEGER,
                refresh_token TEXT,
                scope TEXT
            )
            """

    cursor.execute(query)
    cursor.close()
    connection.close()


def setUser(userId, accessToken, expiresIn, refreshToken, scope):
    _createTable()

    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    timeFetched = ''

    query = """
        INSERT INTO 
            user_table(
                user_id,
                access_token,
                expires_in,
                refresh_token,
                scope
            )
        VALUES 
            (?,?,?,?,?);
    """

    data_tuple = (userId, accessToken, expiresIn, refreshToken, scope)

    cursor.execute(query, data_tuple)
    connection.commit()

    cursor.close()
    connection.close()


def getUserDetails(userId, field="*"):
    _createTable()

    print("USER ID IS: " + userId)

    connection = sqlite3.connect('user.db')
    cursor = connection.cursor()

    # how to select a field using the field parameter
    try:
        query = """
            SELECT * FROM user_table WHERE user_id=?;
        """
        cursor.execute(query, [userId])

    except error:
        print(error)
        return None

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return result
