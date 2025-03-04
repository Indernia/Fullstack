from flask import Flask, jsonify, request
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
    name = request.form["name"]
    email = request.form["email"]

    insert_db(
            'INSERT INTO User (name, email) VALUES (?,?)',
            args=(name, email))
    return '', 200

@app.route('/users/<user_id>/update', methods=["PUT"])
def update_user(user_id):
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        #jsonify({"error": "Name and email are required"})
        return '', 400

    # Update user in the database
    insert_db(
        """UPDATE User SET name = ?, email = ? WHERE id = ?""", 
        args=(name, email, user_id)
        )

    #jsonify({"message": "User updated successfully"})
    return '', 200

@app.route('/users/<user_id>', methods=["DELETE"])
def delete_user(user_id):
    try:
        query_db('DELETE FROM User WHERE id = ?', args=(user_id,))

        #jsonify({"message": "User deleted successfully"})
        return '', 200
    except Exception as e:
        #jsonify({"error": str(e)})
        return '', 500

@app.route('/restaurant/<restaurantID>/menus')
def getRestaurantMenus(restaurantID):
    request = query_db("""
                       SELECT *
                       FROM Menu
                       WHERE restaurantID = ?
                       """, args=(restaurantID))
    return request


@app.route('/menus/<menuID>/sections')
def getSections(menuID):
    request = query_db("""
                          SELECT *
                        FROM MenuSection
                        WHERE menuID = ?
                       """, args=(menuID))
    return request


@app.route('/menuItems/<sectionID>')
def getMenuItems(sectionID):
    request = query_db("""
                        SELECT *
                        FROM MenuItem
                        WHERE sectionID = ?
                       """, args=(sectionID))
    return request




if __name__ == '__main__':
    app.run(port=8080)
