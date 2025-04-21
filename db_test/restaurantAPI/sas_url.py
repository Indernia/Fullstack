from flask import Blueprint, request, jsonify
from database import query_db, insert_db
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions
from datetime import datetime, timedelta
from app import app
import os

sas_url_blueprint = Blueprint('sas_url', __name__)

# Get your Azure credentials from environment variables
account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
account_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
container_name = "menu-items" 
from flask_jwt_extended import jwt_required, get_jwt_identity


# Generate SAS URL for image upload
@app.route('/SASURL', methods=['POST'])
@jwt_required()
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
            expiry=sas_expiration
        )
    except Exception as e:
        return jsonify({"error": f"Error generating SAS token: {str(e)}"}), 500
    
    # Return the SAS URL (with the SAS token) and update menu items photolink
    sas_url = f"{blob_client.url}?{sas_token}"
    insert_db("UPDATE MenuItem SET photoLink = %s WHERE id = %s", args=(blob_client.url, itemID))
    return jsonify({"sasUrl": sas_url})