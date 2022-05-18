from datetime import datetime
from dateutil.relativedelta import relativedelta
from googleapiclient.discovery import build

from gmail_notification_to_mattermost.lib.gmail import get_credential, get_message_ids, get_mail

LABELS = [
    ['Spacee/GitHub'],
    ['Spacee/Backlog']
]


def main():

    end_datetime = datetime.now()
    start_datetime = end_datetime - relativedelta(days=30)

    creds = get_credential()

    service = build('gmail', 'v1', credentials=creds, cache_discovery=False)

    for labels in LABELS:
        message_ids = get_message_ids(
            service=service,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            flags=['is:important'],
            labels=labels)
        print(message_ids)


if __name__ == '__main__':
    main()
