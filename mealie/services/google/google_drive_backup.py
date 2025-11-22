import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from mealie.services._base_service import BaseService


class GoogleDriveBackup(BaseService):
    SCOPES = ["https://www.googleapis.com/auth/drive.file"]

    def __init__(self, credentials_path: str = "credentials.json", token_path: str = "token.json"):
        super().__init__()
        self.credentials_path = credentials_path
        self.token_path = token_path

        self.service = None

    def authenticate(self):
        """Authenticate the user and return a Google Drive service object."""
        try:
            creds = None
            # token.json stores the user's access and refresh tokens.
            if os.path.exists(self.token_path):
                creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)

            # If there are no valid credentials, prompt user to log in.
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Opens a browser window for OAuth login
                    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", self.SCOPES)
                    creds = flow.run_local_server(port=0)

                # Save the credentials for next time
                with open("token.json", "w") as token:
                    token.write(creds.to_json())

            service = build("drive", "v3", credentials=creds)
            self.service = service
            return service

        except Exception as e:
            self.logger.error(f"ERROR: {e}")
            return None

    def upload(self, file_path, file_name, folder_id=None):
        """Upload to Google Drive only if credentials exist."""

        if not os.path.exists(self.credentials_path):
            self.logger.info("Credentials for Google Drive not found. Backup will not be uploaded to Google Drive")
            return None

        if not self.service:
            self.authenticate()

        try:
            file_metadata = {"name": file_name}
            if folder_id:
                file_metadata["parents"] = [folder_id]

            media = MediaFileUpload(file_path, mimetype="application/zip", resumable=True)

            file = self.service.files().create(body=file_metadata, media_body=media, fields="id").execute()

            self.logger.info("Backup file successfully uploaded to Google Drive")
            return file.get("id")

        except HttpError as error:
            self.logger(f"ERROR: {error}")
            return None
