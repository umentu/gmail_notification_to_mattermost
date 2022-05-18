from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path
import pickle
import os
from typing import List, Dict
from datetime import datetime
import base64
import logging
from apiclient import errors

logger = logging.getLogger(__name__)


SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify"
]

PROJECT_DIR = Path(__file__).absolute().parent.parent.parent
TOKEN_PATH = PROJECT_DIR / 'token.pickle'
CREDENTIALS_PATH = PROJECT_DIR / 'credentials.json'


def decode_base64url_data(data):
    """
    base64url のデコード
    """
    decoded_bytes = base64.urlsafe_b64decode(data)
    decoded_message = decoded_bytes.decode("UTF-8")
    return decoded_message


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


def get_message_ids(
        service,
        user_id: str = 'me',
        start_datetime: datetime = datetime(1980, 1, 1, 0, 0, 0),
        end_datetime: datetime = datetime(2200, 1, 1, 0, 0, 0),
        flags: List[str] = [],
        labels: list[str] = []):
    """ Get the IDs of the target mail.

    Args:
        service (_type_): Gmail Service
        user_id (str, optional): The User ID to be obtain. Defaults to 'me'
        start_datetime (datetime, optional): A start time of search. Defaults to datetime(1980, 1, 1, 0, 0, 0).
        end_datetime (datetime, optional): A end time of search. Defaults to datetime(2200, 1, 1, 0, 0, 0).
        flags (List[str], optional):  Gmail API Flags. Defaults to [].
        labels (list[str], optional): Gmail Labels. Defaults to [].

    Returns:
        _type_: _description_
    """

    query: str = ""
    if start_datetime != datetime(1980, 1, 1, 0, 0, 0):
        query += f'after:{int(start_datetime.timestamp())} '

    if end_datetime != datetime(2200, 1, 1, 0, 0, 0):
        query += f'before:{int(end_datetime.timestamp())} '

    query += ''.join(flags) + ' '

    query += ''.join([f'label:{s}' for s in labels]) + ' '
    print(query)

    message_ids = service.users().messages().list(
        userId=user_id, maxResults=100, q=query).execute()

    return message_ids


def get_mail(service, message_ids: Dict):
    """ Get e-mail from Gmail.
    Args:
        service (_type_): Gmail service.
        message_ids (List): target e-mail ids for Gmail.

    """

    messages = []
    try:

        if message_ids["resultSizeEstimate"] == 0:
            logger.warning("no result data!")
            return []

        # message id を元に、message の内容を確認
        for message_id in message_ids["messages"]:
            message_detail = (
                service.users()
                .messages()
                .get(userId="me", id=message_id["id"])
                .execute()
            )
            message = {}

            # 単純なテキストメールの場合
            if 'data' in message_detail['payload']['body']:
                message["body"] = decode_base64url_data(
                    message_detail["payload"]["body"]["data"]
                )
            # html メールの場合、plain/text のパートを使う
            else:
                parts = message_detail['payload']['parts']
                parts = [
                    part for part in parts if part['mimeType'] == 'text/plain']
                message["body"] = decode_base64url_data(
                    parts[0]['body']['data']
                )
            # payload.headers[name: "Subject"]
            message["subject"] = [
                header["value"]
                for header in message_detail["payload"]["headers"]
                if header["name"] == "Subject"
            ][0]
            # payload.headers[name: "From"]
            message["from"] = [
                header["value"]
                for header in message_detail["payload"]["headers"]
                if header["name"] == "From"
            ][0]
            logger.info(message_detail["snippet"])
            messages.append(message)
        return messages

    except errors.HttpError as error:
        print("An error occurred: %s" % error)
