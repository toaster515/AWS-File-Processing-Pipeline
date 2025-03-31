import os
from flask import current_app
from azure.storage.blob import BlobServiceClient
from app.services.storage.storage_interface import StorageInterface

class BlobStorageService(StorageInterface):
    def __init__(self):
        self.connection_string = current_app.config['AZURE_STORAGE_CONNECTION_STRING']
        self.container_name = current_app.config['AZURE_STORAGE_CONTAINER']
        self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)

    def upload_file(self, file, object_key: str) -> str:
        try:
            blob_client = self.container_client.get_blob_client(object_key)
            blob_client.upload_blob(file, overwrite=True)
            url = blob_client.url
            return url
        except Exception as e:
            raise Exception(f"Failed to upload to Azure Blob Storage: {e}")
