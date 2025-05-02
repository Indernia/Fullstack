from flask import Blueprint, request, jsonify
from database import query_db, insert_db
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from flasgger import swag_from
import os

sas_url_blueprint = Blueprint('sas_url', __name__)

# Get your Azure credentials from environment variables
account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
account_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
container_name = "menu-items" 


# Generate SAS URL for image upload
@sas_url_blueprint.route('/SASURL', methods=['POST'])
@jwt_required()
@swag_from({
    'tags': ['SAS URL Generation'],
    'summary': 'Generate a SAS URL for uploading a file to Azure Blob Storage',
    'description': 'This endpoint generates a Shared Access Signature (SAS) URL for a file upload and updates the photoLink in the database.',
    'security': [{'BearerAuth': []}],
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'fileName': {
                        'type': 'string',
                        'example': 'example.jpg',
                        'description': 'The name of the file to upload.'
                    },
                    'itemID': {
                        'type': 'string',
                        'example': '123',
                        'description': 'The ID of the item to associate the uploaded file with.'
                    }
                },
                'required': ['fileName', 'itemID']
            }
        }
    ],
    'responses': {
        200: {
            'description': 'SAS URL successfully generated.',
            'schema': {
                'type': 'object',
                'properties': {
                    'sasUrl': {
                        'type': 'string',
                        'example': 'https://youraccount.blob.core.windows.net/container/example.jpg?sv=...'
                    }
                }
            }
        },
        400: {
            'description': 'Missing required fields in the request body.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        },
        500: {
            'description': 'Internal server error occurred while generating SAS URL.',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def generate_sas_url():
    file_name = request.json.get("fileName")
    itemID = request.json.get("itemID")

    if not file_name or not itemID:
        return jsonify({"error": "Missing 'fileName' or 'itemID' in the request."}), 400

    # Initialize the BlobServiceClient
    try:
        blob_service_client = BlobServiceClient(
            account_url=f"https://{account_name}.blob.core.windows.net", 
            credential=account_key
        )
    except Exception as e:
        return jsonify({"error": f"Error initializing BlobServiceClient: {str(e)}"}), 500
    
    # Get the Blob client for the specific file
    blob_client = blob_service_client.get_blob_client(
        container=container_name, 
        blob=file_name
    )
    
    # Set SAS expiration time (e.g., 15 minutes)
    sas_expiration = datetime.now() + timedelta(minutes=15)

    try:
        # Generate SAS token with permissions to upload
        sas_token = generate_blob_sas(
            account_name=account_name,
            container_name=container_name,
            blob_name=file_name,
            permission=BlobSasPermissions(write=True, create=True),
            expiry=sas_expiration,
            account_key=account_key
        )
    except Exception as e:
        return jsonify({"error": f"Error generating SAS token: {str(e)}"}), 500
    
    # Return the SAS URL (with the SAS token) and update menu items photolink
    sas_url = f"{blob_client.url}?{sas_token}"
    insert_db("UPDATE MenuItem SET photoLink = %s WHERE id = %s", args=(blob_client.url, itemID))
    return jsonify({"sasUrl": sas_url})
