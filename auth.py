import os
import streamlit as st
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/analytics.readonly",
    "https://www.googleapis.com/auth/webmasters.readonly",
]

CLIENT_SECRETS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"

REDIRECT_URI = "http://localhost"


def get_credentials():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_FILE, "w") as f:
                f.write(creds.to_json())
            return creds
        except Exception:
            creds = None

    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    st.markdown("### One-time Google sign-in required")
    st.markdown(f"**1. Click this link and log in:** [Authorize with Google]({auth_url})")
    st.markdown(
        "**2. After clicking Allow, your browser will show a "
        "'This site can't be reached' error — that's expected.**"
    )
    st.markdown(
        "**3. Copy the full URL from your browser's address bar on that error page, "
        "and paste it below:**"
    )

    redirect_response = st.text_input(
        "Paste the full redirected URL here",
        key="oauth_redirect_response",
    )

    if not redirect_response:
        st.stop()

    try:
        flow.fetch_token(authorization_response=redirect_response)
    except Exception as e:
        st.error(f"Couldn't complete sign-in: {e}")
        st.stop()

    creds = flow.credentials
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    st.success("Signed in successfully! Reloading...")
    st.rerun()

    return creds
