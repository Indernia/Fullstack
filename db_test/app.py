from flask import Flask, request
from database import query_db, insert_db

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/users')
def get_users():
    rv = query_db("SELECT * FROM User")
    print(type(rv))
    return rv


@app.route('/users/adduser', methods=["POST"])
def add_user():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]

        insert_db(
                'INSERT INTO User (name, email) VALUES (?,?)',
                args=(name, email))
        return "200"


@app.route('/restaurant/<restaurantID>/menus')
def getRestaurantMenus(restaurantID):
    request = query_db("""
                       SELECT *
                       FROM Menu
                       WHERE restaurantID = ?
                       """, args=(restaurantID))
    return request


if __name__ == '__main__':
    app.run()
