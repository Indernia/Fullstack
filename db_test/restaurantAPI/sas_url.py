from flask import Flask, request, jsonify
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSASPermissions
from datetime import datetime, timedelta
from app import app
import os

# Get your Azure credentials from environment variables
account_name = os.getenv("AZURE_STORAGE_ACCOUNT")
account_key = os.getenv("AZURE_STORAGE_ACCESS_KEY")
container_name = "menu-items"  # Name of your Azure Blob Storage container

# Generate SAS URL for image upload
@app.route('api/SASURL', methods=['POST'])
def generate_sas_url():
    file_name = request.json.get('fileName')  # Get the file name from the frontend

    # Initialize the BlobServiceClient
    blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
    
    # Get the Blob client for the specific file
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    
    # Set SAS expiration time (e.g., 15 minutes)
    sas_expiration = datetime.now() + timedelta(minutes=15)
    
    # Generate SAS token with permissions to upload
    sas_token = generate_blob_sas(
        account_name=account_name,
        container_name=container_name,
        blob_name=file_name,
        permission=BlobSASPermissions(write=True),
        expiry=sas_expiration
    )
    
    # Return the SAS URL (with the SAS token)
    sas_url = f"{blob_client.url}?{sas_token}"
    return jsonify({"sasUrl": sas_url})