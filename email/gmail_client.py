"""Uses Gmail API to read, send, and modify emails."""

import os
import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
TOKEN_PATH = "./CloudStuff/token.json"
CREDS_PATH = "./CloudStuff/credentials.json"
class GmailClient:
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None

        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDS_PATH, SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open(TOKEN_PATH, "w") as token:
                token.write(creds.to_json())

        return build("gmail", "v1", credentials=creds)

    # ---------- READ ----------
    def list_unread_messages(self):
        results = self.service.users().messages().list(
            userId="me",
            q="is:unread"
        ).execute()
        return results.get("messages", [])

    def get_message(self, msg_id):
        return self.service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

    def mark_as_read(self, msg_id):
        self.service.users().messages().modify(
            userId="me",
            id=msg_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

    # ---------- SEND ----------
    def send_reply(self, to_email, subject, body_text):
        message = MIMEText(body_text)
        message["to"] = to_email
        message["subject"] = subject

        raw = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        self.service.users().messages().send(
            userId="me",
            body={"raw": raw}
        ).execute()
