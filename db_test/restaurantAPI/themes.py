from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from
from flask_jwt_extended import jwt_required
import os

themes_blueprint = Blueprint('themes', __name__)


@themes_blueprint.route("/themes/", methods=["GET"])
@swag_from({
    'tags': ['Themes'],
    'summary': 'Retrieve all themes',
    'description': 'Fetch all themes stored in the database.',
    'responses': {
        200: {
            'description': 'List of themes',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'name': {'type': 'string'},
                        'primarycolor': {'type': 'string'},
                        'background': {'type': 'string'},
                        'secondary': {'type': 'string'},
                        'text': {'type': 'string'},
                        'text2': {'type': 'string'},
                        'accent1': {'type': 'string'},
                        'accent2': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def get_themes():
    themes = query_db("""
                        SELECT * FROM themes
                      """)
    return jsonify(themes)


@themes_blueprint.route("/themes/add/", methods=["POST"])
@swag_from({
    'tags': ['Themes'],
    'summary': 'Add a new theme',
    'description': 'Insert a new theme into the database using provided color values.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'primaryColor': {'type': 'string'},
                    'background': {'type': 'string'},
                    'secondary': {'type': 'string'},
                    'text': {'type': 'string'},
                    'text2': {'type': 'string'},
                    'accent1': {'type': 'string'},
                    'accent2': {'type': 'string'}
                },
                'required': ['name', 'primaryColor', 'background', 'secondary', 'text', 'text2', 'accent1', 'accent2']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Theme creation confirmation',
            'schema': {
                'type': 'string',
                'example': 'Added the specified theme'
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def add_theme():
    auth_header = request.headers.get("Authorization")
    key = auth_header.split(" ")[1]
    storedkey = os.getenv("ADMINKEY")
    if key != storedkey:
        return jsonify({"message": "Wrong key"}), 400
    
    data = request.get_json()
    name = data["name"]
    primaryColor = data["primaryColor"]
    background = data["background"]
    secondary = data["secondary"]
    text = data["text"]
    text2 = data["text2"]
    accent1 = data["accent1"]
    accent2 = data["accent2"]
    insert_db("""
                INSERT INTO themes
                (name, primarycolor, background, secondary, text, text2, accent1,accent2)
                VALUES
                (%s, %s, %s, %s, %s, %s, %s, %s)
              """,
              args=(name, primaryColor, background, secondary, text, text2, accent1, accent2)
              )
    return jsonify("Added the specified theme")


@themes_blueprint.route("/themes/delete/<themeName>/", methods=["DELETE"])
@swag_from({
    'tags': ['Themes'],
    'summary': 'Delete a theme by ID',
    'description': 'Deletes a theme from the database using its unique identifier.',
    'parameters': [
        {
            'name': 'themeName',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'The name of the theme to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Theme successfully deleted',
            'schema': {
                'type': 'string',
                'example': 'theme deleted'
            }
        },
        404: {
            'description': 'Theme not found'
        }
    }
})
def delete_theme(themeName):
    auth_header = request.headers.get("Authorization")
    key = auth_header.split(" ")[1]
    storedkey = os.getenv("ADMINKEY")
    if key != storedkey:
        return jsonify({"message": "Wrong key"}), 400
    
    insert_db("""
                DELETE FROM themes WHERE name = %s
              """,
              args=(themeName,)
              )
    return jsonify("theme deleted")


@themes_blueprint.route("/themes/applyThemeToRestaurant/", methods=["POST"])
@jwt_required()
@swag_from({
    'tags': ['Themes'],
    'summary': 'Assign a theme to a restaurant',
    'description': 'Update a restaurant record to apply a specified theme.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'restauntID': {'type': 'integer'},
                    'themeID': {'type': 'integer'}
                },
                'required': ['restauntID', 'themeID']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Theme assignment confirmation',
            'schema': {
                'type': 'string',
                'example': 'Updated theme'
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def assign_theme_to_restaurant():
    data = request.get_json()
    restuarantID = data["restaurantID"]
    themeName = data["themeName"]

    insert_db("""
                UPDATE restaurant SET theme = %s WHERE id = %s
              """,
              args=(themeName, restuarantID)
              )
    return jsonify("Updated theme")

@themes_blueprint.route('/restaurants/theme/<themename>', methods=["GET"])
@swag_from({
        'description': "an endpoint for getting a specific theme",
        'tag': ['Restaurants']
    })
def get_restaurant_theme(themename):
    theme = query_db("SELECT * FROM themes WHERE name = %s", args=(themename,), one=True)
    print(theme)
    return jsonify(theme)


@themes_blueprint.route('/restaurants/themes', methods=["GET"])
@swag_from({
        'description': "an endpoint for getting all themes",
        'tag': ['Restaurants']
    })
def get_all_restaurant_themes():
    names = query_db("SELECT name FROM themes")
    return jsonify(names)
