from io import BytesIO
import os
import uuid
from flask import request, flash, redirect
from werkzeug.utils import secure_filename
from datetime import datetime
from googleapiclient.http import MediaIoBaseUpload
from googleapiclient.discovery import build


# Create a class to encapsulate the file uploading functions and attributes
class GG_DriveFileUploader:
    def __init__(self, flow):
        # Initialize the upload folder and the GoogleAPI object
        self.credentials = flow.credentials

    def upload(self, file):
        """Upload a file using the drive service and the credentials

        Args:
        file: A file from flask app.
        """
        service = build('drive', 'v3', credentials=self.credentials) 

        buffer_memory=BytesIO() 
        file.save(buffer_memory) 

        media_body=MediaIoBaseUpload(file, file.mimetype, resumable=True)  

        created_at= datetime.now().strftime("%Y%m%d%H%M%S") 
        file_metadata={
            "name":f"{file.filename} ({created_at})"
        } 

        returned_fields="id, name, mimeType, webViewLink, exportLinks" 

        upload_response=service.files().create(
            body = file_metadata, 
            media_body=media_body,  
            fields=returned_fields
        ).execute() 

        return upload_response
