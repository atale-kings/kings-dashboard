"""
Handles Google login for the dashboard.

The first time you run the app, this will open a browser tab asking you to
log in with your Google account and click "Allow". After that, it saves a
token file (token.json) so you won't be asked again until the token expires
or you delete that file.

Put your downloaded OAuth "client_secret_....json" file in this same folder
and rename it to: client_secret.json
"""

import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

CLIENT_SECRET_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


def get_credentials():
    """Returns valid Google credentials, logging in via browser if needed."""
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRET_FILE):
                raise FileNotFoundError(
                    f"Could not find '{CLIENT_SECRET_FILE}'. "
                    "Download your OAuth Client JSON from Google Cloud Console "
                    "(APIs & Services -> Credentials) and save it in this folder "
                    f"as '{CLIENT_SECRET_FILE}'."
                )
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return creds
