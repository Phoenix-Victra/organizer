"""Google OAuth 2.0 — gets and refreshes credentials for the Business Profile API."""

import json
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from . import config


def _client_config() -> dict:
    return {
        "installed": {
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }


def get_credentials() -> Credentials:
    """Return valid credentials, running the OAuth flow if token.json is missing."""
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.OAUTH_SCOPES)

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_config(_client_config(), config.OAUTH_SCOPES)
        creds = flow.run_local_server(port=0)

    with open(config.TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

    return creds
