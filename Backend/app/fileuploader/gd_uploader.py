import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from typing import Optional
from dotenv import load_dotenv
import os
from io import BufferedReader
from tusclient import client
from supabase import create_client
load_dotenv()

class GoogleFileUploader:
    def __init__(self):
        self.SCOPES = ["https://www.googleapis.com/auth/drive"]
        self.SERVICE_ACCOUNT = "uploadfile.json"
        self.FOLDER_ID = "1g8nMDoKE-HGCxl1QolkKXQUOD_EepGit"
        
    
    def authenticate(self):
        creds = None
        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", self.SCOPES
            )
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return creds


    def uploadFile(self, filepath):
        creds = self.authenticate()
        service = build("drive", "v3", credentials=creds)
        file_metadata = {"name": filepath,
                        "parents": [self.FOLDER_ID]}
        media = MediaFileUpload(filepath, mimetype="image/*", resumable=True)
        file = (
            service.files()
            .create(body=file_metadata, media_body=filepath)
            .execute() 
        )
        file_id = file.get("id")
        file_link = f"https://drive.google.com/thumbnail?id={file_id}&sz=w500"
        return file_link

class SupaFileUploader:
    def __init__(self):
        self.SUPAAPI = os.getenv("SUPABASEAPIKEY")
        self.PROJECTID = os.getenv("PROJECTID")
        self.BUCKETNAME =os.getenv("BUCKETNAME")
        self.PROJECTURL = f"https://{self.PROJECTID}.storage.supabase.co"
        if self.SUPAAPI:
            self.supabase = create_client(self.PROJECTURL,self.SUPAAPI)
     
    def uploadFile(self, filename:str, file:BufferedReader):
        if self.SUPAAPI:
            my_client = client.TusClient(
                f"{self.PROJECTURL}/storage/v1/upload/resumable",
                headers={"Authorization":self.SUPAAPI, "x-upsert": "true"}
                )
            uploader = my_client.uploader(
                file_stream = file,
                chunk_size=(6 * 1024 * 1024),
                metadata={
                    "bucketName": self.BUCKETNAME,
                    "objectName": filename,
                    "contentType": "image/*",
                    "cacheControl": "3600",
                },
            )
            uploader.upload()
        
    def getPublicUlr(self, filename:str):
        if self.BUCKETNAME:
            publick_url = self.supabase.storage.from_(self.BUCKETNAME).get_public_url(filename)
            return publick_url
    
    