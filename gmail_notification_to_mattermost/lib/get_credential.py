import os
import pickle
from pathlib import Path
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify"
]

PROJECT_DIR = Path(__file__).absolute().parent.parent.parent
TOKEN_PATH = PROJECT_DIR / 'token.pickle'
CREDENTIALS_PATH = PROJECT_DIR / 'credentials.json'


def get_credential():
    """Get Access Token.

    This function saves Access Token in the current directory in pickle format.
    """

    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, 'rb') as token:
            creds = pickle.load(token)
    if creds is None or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_PATH, SCOPES)
            creds = flow.run_console()
        with open(TOKEN_PATH, 'wb') as token:
            pickle.dump(creds, token)
    return creds


if __name__ == '__main__':
    get_credential()
