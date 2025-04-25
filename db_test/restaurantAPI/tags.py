from flask import Blueprint, jsonify, request
from database import query_db, insert_db
from flasgger import swag_from



tags_blueprint = Blueprint('tags', __name__)


@tags_blueprint.route("/tags/", methods=["GET"])
@swag_from({
    'tags': ['Tags'],
    'summary': 'Get all tags',
    'description': 'Retrieve all tags',
    'responses': {
        200: {
            'description': 'List of tags',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'tagType': {'type': 'string'},
                        'tagValue': {'type': 'string'},
                        'tagDescription': {'type': 'string'},
                        'isDeleted': {'type': 'boolean'}
                    }
                }
            }
        }
    }
})
def get_all_tags():
    tags = query_db("""
                    SELECT * FROM tag WHERE isDeleted = false
                    """)
    return jsonify(tags)


@tags_blueprint.route("/tags/create/", methods=["POST"])
@swag_from({
    'tags': ['Tags'],
    'summary': 'Create a new tag',
    'description': 'Create a new tag by providing tagType, tagValue, and tagDescription in the request body.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'tagType': {'type': 'string'},
                    'tagValue': {'type': 'string'},
                    'tagDescription': {'type': 'string'}
                },
                'required': ['tagType', 'tagValue', 'tagDescription']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Confirmation message',
            'schema': {
                'type': 'string',
                'example': 'item added successfully'
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def add_tag():
    data = request.get_json()
    tagType = data["tagType"]
    value = data["tagValue"]
    description = data["tagDescription"]

    insert_db("""
                INSERT INTO tag
                (tagType, TagValue, tagDescription)
                VALUES
                (%s, %s, %s)
              """,
              args=(tagType, value, description)
              )
    return jsonify("item added successfully")


@tags_blueprint.route("/tags/delete/<tagID>/", methods=["DELETE"])
@swag_from({
    'tags': ['Tags'],
    'summary': 'Delete a tag',
    'description': 'Marks a tag as deleted by setting its isDeleted flag to true using its ID.',
    'parameters': [
        {
            'name': 'tagID',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the tag to delete'
        }
    ],
    'responses': {
        200: {
            'description': 'Deletion confirmation',
            'schema': {
                'type': 'string',
                'example': 'deleted tag with id: 1'
            }
        },
        404: {
            'description': 'Tag not found'
        }
    }
})
def delete_tag(tagID):
    insert_db("""
                UPDATE tag
                SET isDeleted = true
                WHERE id = %s
              """,
              args=(tagID,)
              )
    return jsonify(f"deleted tag with id: {tagID}")


@tags_blueprint.route("/tags/addTagToItem/", methods=["POST"])
@swag_from({
    'tags': ['Tags'],
    'summary': 'Add a tag to a menu item',
    'description': 'Associates a tag with a menu item by inserting a record into the menuitemhastag table.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'menuItemID': {'type': 'integer'},
                    'tagID': {'type': 'integer'}
                },
                'required': ['menuItemID', 'tagID']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Confirmation of tag assignment',
            'schema': {
                'type': 'string',
                'example': 'successfully added tag with id 2 to menuitem with id 5'
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def add_tag_to_item():
    data = request.get_json()
    menuItemID = data["menuItemID"]
    tagID = data["tagID"]

    insert_db("""
                INSERT INTO menuitemhastag
                (menuItemID, tagID)
                VALUES
                (%s, %s)
                ON CONFLICT (menuItemID, tagID) DO NOTHING
              """,
              args=(menuItemID, tagID))
    return jsonify(f"successfully added tag with id {tagID} to menuitem with id {menuItemID}")


@tags_blueprint.route("/tags/removeTagFromItem/", methods=["DELETE"])
@swag_from({
    'tags': ['Tags'],
    'summary': 'Remove a tag from a menu item',
    'description': 'Removes the association between a tag and a menu item from the menuitemhastag table.',
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'menuItemID': {'type': 'integer'},
                    'tagID': {'type': 'integer'}
                },
                'required': ['menuItemID', 'tagID']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Confirmation of tag removal',
            'schema': {
                'type': 'string',
                'example': 'tag deleted from item'
            }
        },
        400: {
            'description': 'Invalid input'
        }
    }
})
def delete_tag_from_item():
    data = request.get_json()
    menuItemID = data["menuItemID"]
    tagID = data["tagID"]

    insert_db("""
                DELETE FROM
                menuitemhastag
                WHERE
                menuItemID = %s
                AND tagID = %s
              """,
              args=(menuItemID, tagID))
    return jsonify("tag deleted from item")
